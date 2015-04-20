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
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command("db", MigrateCommand)
api = Api(app)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', configs.secret_key)
from app import views
from app import rest
from app import models