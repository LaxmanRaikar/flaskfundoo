


class User(Exception):

    def __init__(self):
        pass

    def login(self, **params):
        # check the user in db
        # authenticate user
        # failed / success
        pass

    def register(self, **kwargs):
        pass

    def forgotPassword(self, params):
        # check by email address
        # check by username
        # if user exists
        pass