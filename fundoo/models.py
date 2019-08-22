import datetime

from app import db, app, login_manager
import jwt
from time import time
from app import migrate
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin, SQLAlchemyStorage
from flask_login import UserMixin
from flask_rbac import RoleMixin

from passlib.hash import pbkdf2_sha256 as sha256




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
    password = db.Column(db.String(100), nullable=False)
    confirm_password = db.Column(db.String(100), nullable=False)
    is_active = db.Column(db.Boolean, default=False, nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def find_by_username(cls, email_id):
        return cls.query.filter_by(email_id=email_id).first()

    @classmethod
    def return_all(cls):
        def to_json(x):
            return {
                'username': x.username,
                'password': x.password
            }
        return {'users': list(map(lambda x: to_json(x), sign_up.query.all()))}

    @staticmethod
    def generate_hash(password):
        return sha256.hash(password)

    @staticmethod
    def verify_hash(password, hash):
        return sha256.verify(password, hash)

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


class book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60), nullable=False)
    description = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return '<title %r>' % self.title


class Mydata(db.Model):
    __abstract__ = True
    created_time = db.Column(db.DateTime())


class register(Mydata):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    email_id = db.Column(db.String(100))
    mobile = db.Column(db.String(100))
    password = db.Column(db.String(100))


roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)





class Role(db.Model, RoleMixin):
    __tablename__ = 'role'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)

    def __str__(self):
        return self.name


class User(db.Model, UserMixin):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(255))
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='joined'))

    def __str__(self):
        return self.email

