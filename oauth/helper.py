"""
A helper class that aims to make oauth slightly better than the 
'brain surgery on a roller coaster' that it is today
"""

import httplib
import urllib2
import time
import oauth

import logging

class RefreshException(Exception):
    pass
class PermissionException(Exception):
    pass

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

    def fetch_token(self, oauth_request, user):
        # returns OAuthToken
        response = self.urlopen(oauth_request.to_url(), user)
        return oauth.OAuthToken.from_string(response.read())

    def urlopen(self, url, user, *args, **kwargs):
        logging.debug(url)
        # print "\n", url
        try :
            response = urllib2.urlopen(url)
        except urllib2.HTTPError, why :
            error = why.headers.get("www-authenticate", None)
            if error:
                if error.find("token_expired") != -1:
                    self.refresh(user)
                    raise RefreshException("New token aquired. Retry")
                if error.find("permission_denied") != -1:
                    raise PermissionException("Permission denied. Probably revoked OAuth: %s" % url)
            why.msg += "\n%s\n%s\n%s" % (url, why.headers, "".join(why.readlines()))
            raise

        return response

    def refresh(self, user):
        if not isinstance(user, self.db.User) : user = self.db.User.get_from_key(user)

        access_token = user.get_access_token()
        request = oauth.OAuthRequest.from_consumer_and_token(
            self.consumer, token=access_token, http_url=self.access_token_url
        )
        request.sign_request(self.signature_method_hmac_sha1, self.consumer, access_token)
        access_token = self.fetch_token(request, user)
        user.set_access_token(access_token)
        user.save()
        return True

    def sign_url(self, url, user, http_method=None, *args, **kwargs):
        if not isinstance(user, self.db.User) : user = self.db.User.get_from_key(user)

        access_token = user.get_access_token()
        request = oauth.OAuthRequest.from_consumer_and_token(
            self.consumer, token=access_token, http_url=url, http_method=http_method, parameters=kwargs
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
      
        user = self.db.User(type=self.type)
        token = self.fetch_token(oauth_request, user)
        user.set_request_token(token)
        user.save()

        oauth_request = oauth.OAuthRequest.from_token_and_callback(token=token, http_url=self.authorization_url)
        return user, oauth_request.to_url()
       

    def verify(self, user, token, verifier=None, *args, **kwargs):
        if not isinstance(user, self.db.User) : user = self.db.User.get_from_key(user)

        request_token = user.get_request_token()
        key = request_token.key
        assert token == request_token.key

        request = oauth.OAuthRequest.from_consumer_and_token(
            self.consumer, token=request_token, verifier=verifier, http_url=self.access_token_url, parameters=kwargs
        )
        request.sign_request(self.signature_method_hmac_sha1, self.consumer, request_token)
        access_token = self.fetch_token(request, user)
        user.set_access_token(access_token)
        user.save()
        return True
        

    def fetch(self, url, user, tries=1, *args, **kwargs):
        try:
            return self.urlopen(self.sign_url(url, user), user, *args, **kwargs)
        except RefreshException, why:
            if tries == 0:
                raise
            return self.fetch(url, user, tries=tries-1, *args, **kwargs)
