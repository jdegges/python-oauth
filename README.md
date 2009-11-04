# EASY python oauth library

This library was born out of pain while using the existing python oauth libraries. It simply makes some helper classes to reduce the mistakes that are made with using the existing library.

Here is how to do 3-legged OAuth in Google App Engine.

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

    import oauth.consumers
    import config

    callback = "http://%s/twitter/callback" % os.environ['HTTP_HOST']
    twitter = oauth.consumers.TwitterOAuthClient(config.twitter.CONSUMER_KEY, config.twitter.CONSUMER_SECRET, callback)
    
    
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

To use it in another setting, you need to write a different db component (oauth.db) and tell the oauth library to use it. Just implement the 2 classes and related methods and everything should just work. Something like:

    import oauth.db.mysql
    import oauth
    oauth.db = oauth.db.mysql

Please post here if you have any issues.
