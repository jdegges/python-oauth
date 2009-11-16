import oauth
import logging
from datetime import datetime

from django.db import models
class Token(models.Model):
    class Meta:
        db_table = 'oauth_token'

    token = models.TextField()
    secret = models.TextField()
    expires_in = models.IntegerField()
    session_handle = models.TextField(null=True)
    type = models.CharField(max_length=20)
   
    @staticmethod
    def from_oauth_token(token, type="unknown"):
        return Token(
            token=token.key,
            secret=token.secret,
            expires_in=token.expires_in,
            session_handle=token.session_handle,
            type=type,
        )

    def makeToken(self):
        return oauth.OAuthToken(self.token, self.secret, self.expires_in, self.session_handle)

    def __unicode__(self):
        return "%s %s..." % (self.type, self.token[:10])


class User(models.Model):
    class Meta:
        db_table = 'oauth_user'

    request_token = models.OneToOneField(Token, related_name="request_user", null=True)
    access_token = models.OneToOneField(Token, related_name="access_user", null=True)
    type = models.CharField(max_length=20)
    primary_key = models.CharField(max_length=20)

    def set_request_token(self, request_token):
        token = Token.from_oauth_token(request_token, type="request")
        token.save()
        """
        try:
            self.request_token and self.request_token.delete()
        except Token.DoesNotExist, why:
            pass
        """
        self.request_token = token
    def set_access_token(self, access_token):
        token = Token.from_oauth_token(access_token, type="access")
        token.save()
        """
        try:
            self.access_token and self.access_token.delete()
        except Token.DoesNotExist, why:
            pass
        """
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
    def get_from_key(key):
        """Given the string from key(), retrive the object from the DB"""
        r = User.objects.all().filter(primary_key=key).get()
        if r :
            return r
        raise Exception("Can't find object with key: %s" % key)

    """
    # Getting weird behaviour, removing for now
    def delete(self):
        if self.request_token:
            self.request_token.delete()
        if self.access_token:
            self.access_token.delete()
        return super(User, self).delete()
    """
    
    def __unicode__(self):
        return "%s %s" % (self.type, self.primary_key)

    def save(self, *args, **kwargs):
        if not self.primary_key:
            import string
            import random
            chars = string.letters + string.digits
            self.primary_key = ''.join(random.sample(chars, 20))
            logging.info("new user (%s): %s" % (self.type, self.primary_key))

        return super(User, self).save(*args, **kwargs)
