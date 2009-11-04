"""
The MIT License

Copyright (c) 2007 Leah Culver

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

Yahoo Specific consumer
"""

import httplib
import urllib2
import time
import oauth


from google.appengine.ext import db
class Token(db.Model):
    """Auth Token.

       Implemented on Appengine DB, but could be stored anywhere that you have available.
       Just implement all the methods in another data store of your choice
    """
    token = db.TextProperty(required=True)
    secret = db.StringProperty(required=True)
    expires_in = db.IntegerProperty()
    session_handle = db.StringProperty()
    type = db.StringProperty(required=True)
    
    def __init__(self, oauth_token, *args, **kwargs):
        if oauth_token:
            kwargs['token'] = oauth_token.key
            kwargs['secret'] = oauth_token.secret
            kwargs['expires_in'] = oauth_token.expires_in
            kwargs['session_handle'] = oauth_token.session_handle
        db.Model.__init__(self, *args, **kwargs)

    def makeToken(self):
        return oauth.OAuthToken(self.token, self.secret, self.expires_in, self.session_handle)
    
    created = db.DateTimeProperty(auto_now_add=True)
    modified = db.DateTimeProperty(auto_now=True)


class User(db.Model):
    request_token = db.ReferenceProperty(Token, collection_name="request_users")
    access_token = db.ReferenceProperty(Token, collection_name="access_users")
    primary_key = db.StringProperty()
    type = db.StringProperty()

    def set_access_token(self, access_token):
        token = Token(access_token, type="access")
        token.put()
        self.access_token = token
    def set_request_token(self, request_token):
        token = Token(request_token, type="request")
        token.put()
        self.request_token = token

    def get_request_token(self):
        return self.request_token.makeToken()
    def get_access_token(self):
        return self.access_token.makeToken()
    def get_key(self):
        """Make this non-guessable as it is the login token for this system"""
        return self.primary_key
    @staticmethod
    def get(key):
        """Given the string from key(), retrive the object from the DB"""
        r = User.all().filter("primary_key =", key).get()
        if r : 
            return r
        raise Exception("Can't find object with key: %s" % key)
    
    def save(self):
        """Save this to the DB"""
        if not self.primary_key:
            import string
            import random
            chars = string.letters + string.digits
            self.primary_key = ''.join(random.sample(chars, 20))
        return self.put()

    created = db.DateTimeProperty(auto_now_add=True)
    modified = db.DateTimeProperty(auto_now=True)


class OAuthClient(oauth.OAuthClient):
    """A client to help simplify the oauth pain"""
    signature_method_hmac_sha1 = oauth.OAuthSignatureMethod_HMAC_SHA1()

    def __init__(self, consumer_key, consumer_secret, callback_url):
        consumer = oauth.OAuthConsumer(consumer_key, consumer_secret)
        self.consumer = consumer
        self.callback_url = callback_url

    @property
    def request_token_url(self):
        raise NotImplemented()
    
    @property
    def authorization_url(self):
        raise NotImplemented()
    
    @property
    def access_token_url(self):
        raise NotImplemented()

    type = "unknown"

    def fetch_token(self, oauth_request):
        # returns OAuthToken
        response = self.urlopen(oauth_request.to_url())
        return oauth.OAuthToken.from_string(response.read())

    def urlopen(self, url, user=None, *args, **kwargs):
        # print "\n%s\n" % url
        try :
            response = urllib2.urlopen(url)
        except urllib2.HTTPError, why :
            error = why.headers.get("www-authenticate", None)
            if why.code == 401 :
                if error.find("token_expired") != -1:
                    if user:
                        self.refresh(user)
                        return self.fetch(url, user, *args, **kwargs)
            if error :
                why.msg = error
            raise why

        return response

    ############ START OF API #############

    def start(self):
        """Starts the authorization process and returns the token, url to give the user"""
        oauth_request = oauth.OAuthRequest.from_consumer_and_token(
            self.consumer, callback=self.callback_url, http_url=self.request_token_url
        )
        oauth_request.sign_request(self.signature_method_hmac_sha1, self.consumer, None)
        token = self.fetch_token(oauth_request)
        oauth_request = oauth.OAuthRequest.from_token_and_callback(token=token, http_url=self.authorization_url)
      
        user = User(type=self.type)
        user.set_request_token(token)
        user.save()

        return user, oauth_request.to_url()
       

    def verify(self, user, token, verifier):
        if type(user) != User : user = User.get(user)

        request_token = user.get_request_token()
        assert token == request_token.key

        request = oauth.OAuthRequest.from_consumer_and_token(
            self.consumer, token=request_token, verifier=verifier, http_url=self.access_token_url
        )
        request.sign_request(self.signature_method_hmac_sha1, self.consumer, request_token)
        access_token = self.fetch_token(request)
        user.set_access_token(access_token)
        user.save()
        return True

    def refresh(self, user):
        if type(user) != User : user = User.get(user)

        access_token = user.get_access_token()
        request = oauth.OAuthRequest.from_consumer_and_token(
            self.consumer, token=access_token, http_url=self.access_token_url
        )
        request.sign_request(self.signature_method_hmac_sha1, self.consumer, access_token)
        access_token = self.fetch_token(request)
        user.set_access_token(access_token)
        user.save()
        return True
        

    def fetch(self, url, user, *args, **kwargs):
        if type(user) != User : user = User.get(user)

        access_token = user.get_access_token()
        request = oauth.OAuthRequest.from_consumer_and_token(
            self.consumer, token=access_token, http_url=url, **kwargs
        )
        request.sign_request(self.signature_method_hmac_sha1, self.consumer, access_token)
        url = request.to_url()
        return self.urlopen(url, user)
