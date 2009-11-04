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
