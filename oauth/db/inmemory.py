users = {}
class User:
    def __init__(self, *args, **kwargs):
        self.primary_key = None
    def set_access_token(self, access_token):
        self.access_token = access_token
    def set_request_token(self, request_token):
        self.request_token = request_token
    def get_request_token(self):
        return self.request_token
    def get_access_token(self):
        return self.access_token
    def get_key(self):
        return self.primary_key
    @staticmethod
    def get(key):
        return users[key]
    def save(self):
        if not self.primary_key:
            import string
            import random
            chars = string.letters + string.digits
            self.primary_key = ''.join(random.sample(chars, 20))
