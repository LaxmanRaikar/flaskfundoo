from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://laxman777:password@localhost/fundooproject'
db = SQLAlchemy(app)
migrate = Migrate(app, db)






