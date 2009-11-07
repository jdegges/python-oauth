"""
A helper class that aims to make oauth slightly better than the 
'brain surgery on a roller coaster' that it is today
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
            import db.inmemory as db
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

    def urlopen(self, url, old_url=None, user=None, *args, **kwargs):
        try :
            response = urllib2.urlopen(url)
        except urllib2.HTTPError, why :
            error = why.headers.get("www-authenticate", None)
            if why.code == 401 :
                if error and error.find("token_expired") != -1:
                    if old_url and user:
                        self.refresh(user)
                        return self.fetch(old_url, user, *args, **kwargs)
            why.msg += "\n%s\n%s\n%s" % (url, why.headers, "".join(why.readlines()))
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

    def sign_url(self, url, user, *args, **kwargs):
        if not isinstance(user, self.db.User) : user = self.db.User.get(user)

        access_token = user.get_access_token()
        request = oauth.OAuthRequest.from_consumer_and_token(
            self.consumer, token=access_token, http_url=url, parameters=kwargs
        )
        request.sign_request(self.signature_method_hmac_sha1, self.consumer, access_token)
        return request.to_url()

    ############ START OF API #############

    def start(self, *args, **kwargs):
        """Starts the authorization process and returns the token, url to give the user"""
        oauth_request = oauth.OAuthRequest.from_consumer_and_token(
            self.consumer, callback=self.callback_url, http_url=self.request_token_url, parameters=kwargs
        )
        oauth_request.sign_request(self.signature_method_hmac_sha1, self.consumer, None)
        token = self.fetch_token(oauth_request)
      
        user = self.db.User(type=self.type)
        user.set_request_token(token)
        user.save()

        oauth_request = oauth.OAuthRequest.from_token_and_callback(token=token, http_url=self.authorization_url)
        return user, oauth_request.to_url()
       

    def verify(self, user, token, verifier=None, *args, **kwargs):
        if not isinstance(user, self.db.User) : user = self.db.User.get(user)

        request_token = user.get_request_token()
        assert token == request_token.key

        request = oauth.OAuthRequest.from_consumer_and_token(
            self.consumer, token=request_token, verifier=verifier, http_url=self.access_token_url, parameters=kwargs
        )
        request.sign_request(self.signature_method_hmac_sha1, self.consumer, request_token)
        access_token = self.fetch_token(request)
        user.set_access_token(access_token)
        user.save()
        return True
        

    def fetch(self, url, user, *args, **kwargs):
        return self.urlopen(self.sign_url(url, user), url, user, *args, **kwargs)
