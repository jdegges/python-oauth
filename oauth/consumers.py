import helper

class YahooOAuthClient(helper.OAuthClient):
    request_token_url = 'https://api.login.yahoo.com/oauth/v2/get_request_token'
    access_token_url  = 'https://api.login.yahoo.com/oauth/v2/get_token'
    authorization_url = 'https://api.login.yahoo.com/oauth/v2/request_auth'
    type = "yahoo"

class TwitterOAuthClient(helper.OAuthClient):
    request_token_url = 'http://twitter.com/oauth/request_token'
    access_token_url  = 'http://twitter.com/oauth/access_token'
    authorization_url = 'http://twitter.com/oauth/authorize'
    type = "twitter"

class MyspaceOAuthClient(helper.OAuthClient):
    request_token_url = 'http://api.myspace.com/request_token'
    access_token_url  = 'http://api.myspace.com/oauth/access_token'
    authorization_url = 'http://api.myspace.com/oauth/authorize'
    type = "myspace"

class GoogleOAuthClient(helper.OAuthClient):
    request_token_url = 'https://www.google.com/accounts/OAuthGetRequestToken'
    access_token_url  = 'https://www.google.com/accounts/OAuthGetAccessToken'
    authorization_url = 'https://www.google.com/accounts/OAuthAuthorizeToken'

    def __init__(self, *args, **kwargs):
        if not kwargs.has_key('scope'):
            raise Exception("No scope attribute")
        self.scope = kwargs['scope']
        del kwargs['scope']
        return super(GoogleOAuthClient, self).__init__(*args, **kwargs)

    def start(self, *args, **kwargs):
        kwargs['scope'] = self.scope
        return super(GoogleOAuthClient, self).start(*args, **kwargs)
