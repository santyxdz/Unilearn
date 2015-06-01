import os
from flask import Flask
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from flask_login import LoginManager
from app import configs

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = configs.SQLALCHEMY_DATABASE_URI
app.secret_key = configs.secret_key
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "home"
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command("db", MigrateCommand)
api = Api(app)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', configs.secret_key)
app.config['OAUTH_CREDENTIALS'] = {
    'facebook': {
        'id': '323621904515839',
        'secret': '3c42b3f4b82545fb7c620f46d925bb19'
    },
    'twitter': {
        'id': 'r134O2NFk7jdcomFWA0UONWiD', #To Check
        'secret': 'QfaXTwAojV8ISMnmfnhos8trHpLh56PR7OqHJ0jXl9vah1yIA2' #To Check
    }
}
from app import models
from app import views
from app import rest
