from  app  import db, app, login_manager
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return sign_up.query.get(int(user_id))

class sign_up(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(60), nullable=False)
    email_id = db.Column(db.String(100), unique=True, nullable=False)
    mobile_no = db.Column(db.String(10), nullable=False)
    password = db.Column(db.String(50), nullable=False)
    confirm_password = db.Column(db.String(50), nullable = False)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        print("klkl",self.id)
        return s.dumps({'user_id': self.id}).decode('utf-8')



    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return sign_up.query.get(user_id)





    def __repr__(self):
        return '<sign_up %r>' % self.username


