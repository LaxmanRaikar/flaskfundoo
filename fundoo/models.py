import datetime
import nexmo
from app import db, app, login_manager

import jwt
from time import time
from flask_login import UserMixin
from flask_rbac import RoleMixin
from passlib.hash import pbkdf2_sha256 as sha256


client = nexmo.Client(key='169b4a9b', secret='yO1QsLp0hB95oPPRkP6DM7vqHqiulQJxuVBZhFIfhUjQMTuATn')


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
    mobile_no = db.Column(db.String(13), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    confirm_password = db.Column(db.String(100), nullable=False)
    is_active = db.Column(db.Boolean, default=False, nullable=False)

    def save_to_db(self):
        """ this method is used to save data in db"""
        db.session.add(self)
        db.session.commit()

    @classmethod
    def find_by_email_id(cls, email_id):
        """ this method is used to find the email_id in the above model class """
        return cls.query.filter_by(email_id=email_id).first()

    @classmethod
    def find_by_mobile(cls, mobile_no):
        """ this method is used to find the mobile_no in the above model class """
        return cls.query.filter_by(mobile_no=mobile_no).first

    @classmethod
    def return_all(cls):
        """ this method returns all the username and password  saved in db """
        def to_json(x):
            return {
                'username': x.username,
                'password': x.password
            }
        return {'users': list(map(lambda x: to_json(x), sign_up.query.all()))}

    @staticmethod
    def generate_hash(password):
        """ this method is used the encode the password """
        return sha256.hash(password)

    @staticmethod
    def verify_hash(password, hash):
        """ this method is used to very the password """
        return sha256.verify(password, hash)

    def generate_token(self, data):
        """ this method is used to generate the jwt token """
        return jwt.encode({'token': data},
                          app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    def get_reset_token(self, expires_in=600):
        print('i am here')
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
    """ this method is used to save the notes for pagination part"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60), nullable=False)
    description = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return '<title %r>' % self.title


class Mydata(db.Model):
    """ this method is used  for inheritance of model class """
    __abstract__ = True
    created_time = db.Column(db.DateTime())


class register(Mydata):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    email_id = db.Column(db.String(100))
    mobile = db.Column(db.String(100))
    password = db.Column(db.String(100))


my_label = db.Table('my_label',
    db.Column('note_id', db.Integer, db.ForeignKey('notes.id'), primary_key=True),
    db.Column('label_id', db.Integer, db.ForeignKey('label.id'), primary_key=True)
)

my_collab = db.Table('my_collab',
    db.Column('note_id', db.Integer, db.ForeignKey('notes.id'), primary_key=True),
    db.Column('collab_id', db.Integer, db.ForeignKey('collabrator.id'), primary_key=True)
)


class Notes(db.Model):
    """ this class is used to store the notes"""

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    title = db.Column(db.String(100))
    description = db.Column(db.String(5000))
    color = db.Column(db.String, default=False)
    image = db.Column(db.String(100), default=False)
    is_archive = db.Column(db.Boolean, default=False)
    is_pinned = db.Column(db.Boolean, default=False)
    is_trash = db.Column(db.Boolean, default=False)
    remainder = db.Column(db.DateTime, default=None)
    created_time = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    label = db.relationship('Label', secondary=my_label, lazy='subquery', backref=db.backref('labels', lazy=True))
    collabrator = db.relationship('Collabrator', secondary=my_collab, lazy='subquery', backref=db.backref('collab', lazy=True))

    def __repr__(self):
        return '<Notes %r>' % self.title

    def save_to_db(self):
        """ this method is used to save data in db"""
        db.session.add(self)
        db.session.commit()

    def delete_data(self):
        """ this method is used to delete the note"""
        db.session.delete(self)
        db.session.commit()


    @classmethod
    def find_user_id(cls, user_id):
        """ this method is used to find the email_id in the above model class """
        return cls.query.filter_by(user_id=user_id).all()

    @classmethod
    def return_all(cls):
        """ this method returns all the username and password  saved in db """

        def to_json(x):
            return {
                'title': x.title,
                'description': x.description,
                'color': x.color,
                'image': x.image,
                'is_archieve': x.is_archieve,
                'is_pinned': x.is_pinned,
                'is_trash': x.is_trash,
                'remainder': x.remainder
            }
        return {'notes': list(map(lambda x: to_json(x), Notes.query.all()))}


class Label(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(200), default=False)


class Collabrator(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    collabrator = db.Column(db.String(200), default=False)


class ok(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    remainder=db.Column(db.DateTime, default=None)
    title = db.Column(db.String, default=None)