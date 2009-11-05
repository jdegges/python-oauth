import oauth.helper
import oauth.db.inmemory

class TestOAuthClient(oauth.helper.OAuthClient):
    request_token_url = 'http://term.ie/oauth/example/request_token.php'
    access_token_url  = 'http://term.ie/oauth/example/access_token.php'
    authorization_url = '' # only for 3 legged oauth
    type = "yahoo"

# key and secret granted by the service provider for this consumer application
CONSUMER_KEY = 'key'
CONSUMER_SECRET = 'secret'

def run_two_legged():
    # setup
    print '** OAuth Python Library Example **'
    client = TestOAuthClient(CONSUMER_KEY, CONSUMER_SECRET, callback_url=None, db=oauth.db.inmemory)
    pause()

    # get request token
    print '* Obtain a request token ...'
    pause()
    user, url = client.start()
    
    token = user.get_request_token()
    print 'GOT'
    print 'key: %s' % str(token.key)
    print 'secret: %s' % str(token.secret)
    print 'callback confirmed? %s' % str(token.callback_confirmed)
    pause()

    print '* Obtain an access token ...'
    pause()
    client.verify(user, token.key)

    token = user.get_access_token()
    print 'GOT'
    print 'key: %s' % str(token.key)
    print 'secret: %s' % str(token.secret)
    pause()

    # access some protected resources
    print '* Access protected resources ...'
    pause()

    data = client.fetch("http://term.ie/oauth/example/echo_api.php?paul=awesome", user)
    
    print 'GOT'
    print 'data: %s' % data.read()
    pause()

def pause():
    print ''
    import time
    # time.sleep(1)

if __name__ == '__main__':
    run_two_legged()
    print 'Done.'
