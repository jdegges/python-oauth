import sys
import unittest
import oauth.consumer
import config

class TestClient(unittest.TestCase):
    pass


class TestClient(unittest.TestCase):

    def oauth(self, consumer, keys, threeleg, test_url, **kwargs):
        self.client = consumer(keys.CONSUMER_KEY, keys.CONSUMER_SECRET, callback_url='oob', **kwargs)
        user, url = self.client.start()
        if threeleg:
            print "Get the token from this url:\n%s\nToken: " % url
            verify = sys.stdin.readline().strip()
        else:
            verify = None
        token = user.get_request_token()
        self.client.verify(user, token.key, verify)
        if test_url:
            print user.get_access_token(), verify
            response = self.client.fetch(test_url, user)
            print response.read()

class Yahoo(TestClient):
    
    def test_2leg(self):
        self.oauth(oauth.consumer.Yahoo, config.yahoo2leg, False, "http://query.yahooapis.com/v1/yql?q=select%20*%20from%20xml%20where%20url%3D'http%3A%2F%2Frss.news.yahoo.com%2Frss%2Ftopstories'&format=json")

    def test_3leg(self):
        self.oauth(oauth.consumer.Yahoo, config.yahoo3leg, True, "http://social.yahooapis.com/v1/me/guid?format=json")


class Twitter(TestClient):

    def test_oauth(self):
        self.oauth(oauth.consumer.Twitter, config.twitter, True, "http://twitter.com/account/verify_credentials.json")

class Google(TestClient):

    def test_oauth(self):
        self.oauth(oauth.consumer.Google, config.google, True, "http://www.blogger.com/feeds/default/blogs", scope="http://www.blogger.com/feeds/")

# myspace doesn't support oob auth
#class Myspace(TestClient):
#    def test_oauth(self):
#        self.oauth(oauth.consumer.Myspace, config.myspace, True, "")


if __name__ == '__main__':
    unittest.main()
