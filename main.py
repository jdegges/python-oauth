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

