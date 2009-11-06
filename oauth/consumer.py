import helper

class Yahoo(helper.OAuthClient):
    request_token_url = 'https://api.login.yahoo.com/oauth/v2/get_request_token'
    access_token_url  = 'https://api.login.yahoo.com/oauth/v2/get_token'
    authorization_url = 'https://api.login.yahoo.com/oauth/v2/request_auth'
    type = "yahoo"

class Twitter(helper.OAuthClient):
    request_token_url = 'http://twitter.com/oauth/request_token'
    access_token_url  = 'http://twitter.com/oauth/access_token'
    authorization_url = 'http://twitter.com/oauth/authorize'
    type = "twitter"

class Myspace(helper.OAuthClient):
    request_token_url = 'http://api.myspace.com/request_token'
    access_token_url  = 'http://api.myspace.com/access_token'
    authorization_url = 'http://api.myspace.com/authorize'
    type = "myspace"

class Google(helper.OAuthClient):
    request_token_url = 'https://www.google.com/accounts/OAuthGetRequestToken'
    access_token_url  = 'https://www.google.com/accounts/OAuthGetAccessToken'
    authorization_url = 'https://www.google.com/accounts/OAuthAuthorizeToken'

    def __init__(self, *args, **kwargs):
        if not kwargs.has_key('scope'):
            raise Exception("No scope attribute")
        self.scope = kwargs['scope']
        del kwargs['scope']
        return super(Google, self).__init__(*args, **kwargs)

    def start(self, *args, **kwargs):
        kwargs['scope'] = self.scope
        return super(Google, self).start(*args, **kwargs)
