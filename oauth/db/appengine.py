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
        super(Token, self).__init__(*args, **kwargs)

    def makeToken(self):
        return oauth.OAuthToken(self.token, self.secret, self.expires_in, self.session_handle)
    
    created = db.DateTimeProperty(auto_now_add=True)
    modified = db.DateTimeProperty(auto_now=True)


class User(db.Model):
    request_token = db.ReferenceProperty(Token, collection_name="request_users")
    access_token = db.ReferenceProperty(Token, collection_name="access_users")
    primary_key = db.StringProperty()
    type = db.StringProperty()

    def set_request_token(self, request_token):
        token = Token(request_token, type="request")
        token.put()
        if self.request_token:
            self.request_token.delete()
        self.request_token = token
    def set_access_token(self, access_token):
        token = Token(access_token, type="access")
        token.put()
        if self.access_token:
            self.access_token.delete()
        self.access_token = token

    def get_request_token(self):
        token =  self.request_token
        if token:
            return token.makeToken()
        return token
    def get_access_token(self):
        token =  self.access_token
        if token:
            return token.makeToken()
        return token
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
    def delete(self):
        if self.request_token:
            self.request_token.delete()
        if self.access_token:
            self.access_token.delete()
        return super(User, self).delete()

    created = db.DateTimeProperty(auto_now_add=True)
    modified = db.DateTimeProperty(auto_now=True)
