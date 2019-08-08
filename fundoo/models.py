import datetime

from  app  import db, app, login_manager

from flask_login import UserMixin
import jwt
from time import time

from itsdangerous import Serializer


@login_manager.user_loader
def load_user(user_id):
    """
      Flask-Login user_loader callback.
      The user_loader function asks this function to get a User Object or return
      None based on the userid.
      The userid was stored in the session environment by Flask-Login.
      user_loader stores the returned User object in current_user during every
      flask request.
      """
    return sign_up.query.get(int(user_id))


class sign_up(db.Model, UserMixin):
    """ db for to register the users
    UserMixin provides default implementations for the methods that Flask-Login expects user objects to have"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(60), nullable=False)
    email_id = db.Column(db.String(100), unique=True, nullable=False)
    mobile_no = db.Column(db.String(10), nullable=False)
    password = db.Column(db.String(50), nullable=False)
    confirm_password = db.Column(db.String(50), nullable=False)
    is_active = db.Column(db.Boolean, default=False, nullable=False)

    def get_reset_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return sign_up.query.get(id)


    def __repr__(self):
        return '<sign_up %r>' % self.username


