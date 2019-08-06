from  app  import db

class sign_up(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(60), nullable=False)
    email_id = db.Column(db.String(100), unique=True, nullable=False)
    mobile_no = db.Column(db.String(10), nullable=False)
    password = db.Column(db.String(50), nullable=False)
    confirm_password = db.Column(db.String(50), nullable = False)

    def __repr__(self):
        return '<sign_up %r>' % self.username


