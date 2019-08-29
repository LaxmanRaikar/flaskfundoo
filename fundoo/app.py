import os
import dotenv
from flask import Flask
from celery import Celery
from flask_rbac import RBAC
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from elasticsearch import Elasticsearch
from flask_login import LoginManager
from flask_shorturl import ShortUrl
from flask_dance.contrib.github import make_github_blueprint
from flask_dance.contrib.linkedin import make_linkedin_blueprint
from flask_dance.contrib.dropbox import make_dropbox_blueprint
from flask_dance.contrib.twitter import make_twitter_blueprint

github_blueprint = make_github_blueprint(client_id=os.environ.get('GITHUB_OAUTH_CLIENT_KEY'),
                                         client_secret=os.environ.get('GITHUB_OAUTH_SECRET_KEY'))
linked_blueprint = make_linkedin_blueprint(client_id=os.environ.get('LINKED_OAUTH_CLIENT_KEY'), client_secret=os.environ.get('LINKED_OAUTH_SECRET_KEY'))
dropbox_blueprint = make_dropbox_blueprint(app_key=os.environ.get('DROPBOX_OAUTH_CLIENT_KEY'), app_secret=os.environ.get('DROPBOX_OAUTH_SECRET_KEY'))
twitter_blueprint = make_twitter_blueprint(api_key=os.environ.get('TWITTER_OAUTH_CLIENT_KEY'), api_secret=os.environ.get('TWITTER_OAUTH_SECRET_KEY'))
dotenv.load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://laxman777:password@localhost/fundooproject'

db = SQLAlchemy(app)
es = Elasticsearch()

bcrypt = Bcrypt(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
su = ShortUrl(app)
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER')

app.config['MAIL_PORT'] = os.environ.get('MAIL_PORT')
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

app.config['RBAC_USE_WHITE'] = True


app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
app.register_blueprint(linked_blueprint, url_prefix='/linked_login')
app.register_blueprint(github_blueprint, url_prefix='/github_login')
app.register_blueprint(dropbox_blueprint, url_prefix='/dropbox_login')
app.register_blueprint(twitter_blueprint, url_prefix='/twitter_login')
# rbac = RBAC(app)
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)
mail = Mail(app)










