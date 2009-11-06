# EASY python oauth library

This library was born out of pain while using the existing python oauth libraries. It simply makes some helper classes to reduce the mistakes that are made with using the existing library.

# 3 Methods to care about

## def start():

Starts the process with your provider. @return (user, url). Give the `user.get_key()` string as a cookie, and redirect them to the url.

## def verify(user, token, verifier):

Verifies the user authorized your correctly. The parameters are

* user - The `user.get_key()` from the `start()` method
* token - The GET parameter `oauth_token`
* verifier - The GET parameter `oauth_verifier`

## def fetch(url, user):

Does an oauth authenticated fetch. @return a file-like object from `urllib2.urlopen()`. The paremters

* url - The remote url to request
* user - The `user.get_key()` from the `start()` method

And that's it!

# Examples

## 3-legged OAuth with Out of Band callback

config.py
    
    class twitter:
        CONSUMER_KEY = 'put_yours'
        CONSUMER_SECRET = 'put_yours'

test.py

    import sys
    import oauth.consumer
    import config

    def do_oauth():
        client = oauth.consumer.Twitter(config.twitter.CONSUMER_KEY, config.twitter.CONSUMER_SECRET, callback_url='oob')
        user, url = client.start()

        # the next 3 lines are for oob auth (normally done by a callback and then the `token` and `key` are request params)
        print "Get the token from this url:\n%s\nToken: " % url
        verify = sys.stdin.readline().strip()
        token = user.get_request_token()

        client.verify(user, token.key, verify)
        response = client.fetch("http://twitter.com/account/verify_credentials.json", user)
        print response.read()

    do_oauth()

## 3-legged OAuth in Google App Engine

    $ cp google_appengine/new_project_template cool_oauth_app
    $ cd cool_oauth_app
    $ git clone git@github.com:ptarjan/python-oauth.git
    $ ln -s python-oauth/oauth

config.py
    
    class twitter:
        CONSUMER_KEY = 'put_yours'
        CONSUMER_SECRET = 'put_yours'

main.py

    import os

    import wsgiref.handlers

    from google.appengine.ext import webapp

    import oauth.consumer
    import oauth.db.appengine
    import config

    callback = "http://%s/twitter/callback" % os.environ['HTTP_HOST']
    twitter = oauth.consumer.Twitter(config.twitter.CONSUMER_KEY, config.twitter.CONSUMER_SECRET, callback, db=oauth.db.appengine)
    
    
    class MainHandler(webapp.RequestHandler):
        
        def get(self):
            self.redirect('/twitter')


    class TwitterHandler(webapp.RequestHandler):

        def get(self):
            user, url = twitter.start()
            self.redirect(url)
            self.response.headers.add_header(
                'Set-Cookie',
                'twitter=%s; expires=Fri, 31-Dec-2038 23:59:59 GMT' \
                    % user.get_key().encode())


    class TwitterCallbackHandler(webapp.RequestHandler):
        
        def get(self):
            token = self.request.get("oauth_token")
            verifier = self.request.get("oauth_verifier", None)
            user = self.request.cookies.get("twitter")
            twitter.verify(user, token, verifier)
            self.redirect("/test")


    class TestHandler(webapp.RequestHandler):

        def get(self):
            user = self.request.cookies.get("twitter")
            result = twitter.fetch(
                "http://twitter.com/account/verify_credentials.json", user)
            self.response.out.write(result.read().replace("<", "&lt;"))

    def main():
        application = webapp.WSGIApplication([
                                            ('/', MainHandler),
                                            ('/twitter', TwitterHandler),
                                            ('/twitter/callback', TwitterCallbackHandler),
                                            ('/test', TestHandler),
                                           ],
                                           debug=True)
        wsgiref.handlers.CGIHandler().run(application)


    if __name__ == '__main__':
        main()

To use it in another setting, you need to write a different db component (oauth.db) and tell the oauth library to use it. Just implement the User class and related methods and everything should just work. Something like:

    import oauth.db.mysql as db
    db.user = 'foo'
    db.pass = 'bar'
    twitter = oauth.consumer.Twitter(config.twitter.CONSUMER_KEY, config.twitter.CONSUMER_SECRET, callback, db=db)

Please post here if you have any issues.
