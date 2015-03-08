import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

app = Flask(__name__)
##app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
#app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
#app.secret_key = config.secretKey
#db = SQLAlchemy(app)
#migrate = Migrate(app, db)
#manager = Manager(app)
#manager.add_command("db", MigrateCommand)

from app import configs
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', configs.secret_key)
from app import views
from app import models