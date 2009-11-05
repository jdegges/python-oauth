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

class OAuthClient(oauth.OAuthClient):
    """A client to help simplify the oauth pain"""
    signature_method_hmac_sha1 = oauth.OAuthSignatureMethod_HMAC_SHA1()

    def __init__(self, consumer_key, consumer_secret, callback_url, db=None):
        consumer = oauth.OAuthConsumer(consumer_key, consumer_secret)
        self.consumer = consumer
        self.callback_url = callback_url
        if not db :
            import db.appengine as db
        self.db = db

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
        try :
            response = urllib2.urlopen(url)
        except urllib2.HTTPError, why :
            error = why.headers.get("www-authenticate", None)
            if why.code == 401 :
                if error and error.find("token_expired") != -1:
                    if user:
                        self.refresh(user)
                        return self.fetch(url, user, *args, **kwargs)
            if error :
                why.msg = error
            raise why

        return response

    def refresh(self, user):
        if not isinstance(user, self.db.User) : user = self.db.User.get(user)

        access_token = user.get_access_token()
        request = oauth.OAuthRequest.from_consumer_and_token(
            self.consumer, token=access_token, http_url=self.access_token_url
        )
        request.sign_request(self.signature_method_hmac_sha1, self.consumer, access_token)
        access_token = self.fetch_token(request)
        user.set_access_token(access_token)
        user.save()
        return True

    ############ START OF API #############

    def start(self):
        """Starts the authorization process and returns the token, url to give the user"""
        oauth_request = oauth.OAuthRequest.from_consumer_and_token(
            self.consumer, callback=self.callback_url, http_url=self.request_token_url
        )
        oauth_request.sign_request(self.signature_method_hmac_sha1, self.consumer, None)
        token = self.fetch_token(oauth_request)
      
        user = self.db.User(type=self.type)
        user.set_request_token(token)
        user.save()

        oauth_request = oauth.OAuthRequest.from_token_and_callback(token=token, http_url=self.authorization_url)
        return user, oauth_request.to_url()
       

    def verify(self, user, token, verifier=None):
        if not isinstance(user, self.db.User) : user = self.db.User.get(user)

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
        

    def fetch(self, url, user, *args, **kwargs):
        if not isinstance(user, self.db.User) : user = self.db.User.get(user)

        access_token = user.get_access_token()
        request = oauth.OAuthRequest.from_consumer_and_token(
            self.consumer, token=access_token, http_url=url, **kwargs
        )
        request.sign_request(self.signature_method_hmac_sha1, self.consumer, access_token)
        url = request.to_url()
        return self.urlopen(url, user)
