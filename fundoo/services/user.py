from models import sign_up
from app import db


class User:

    def __init__(self, username=None, password=None, email_id=None, mobile_no=None, confirm_password=None):
        """ parameterized constructor"""
        self.username = username
        self.password = password
        self.email_id = email_id
        self.mobile_no = mobile_no
        self.confirm_password = confirm_password

    def login(self):
        """ this method is used to query with db for login
        :param:email_id,password
        :return: login value"""
        login = sign_up.query.filter_by(email_id=self.email_id, password=self.password, is_active=True).first()
        return login

    def register(self):
        """ this method is used to save the user details in db for registration
            :param:username,email_id,mobile_no,password, confirm_password """

        add = sign_up(username=self.username, email_id=self.email_id, mobile_no=self.mobile_no,
                      password=self.password, confirm_password=self.confirm_password)
        db.session.add(add)  # saving data to db
        db.session.commit()

    def forgotPassword(self):
        """ this method is used to query the db field for reset password
        :param:email_id
        :return: user is present in db or not"""
        user = sign_up.query.filter_by(email_id=self.email_id).first()
        return user

    def Profilepic(self):
        pass

