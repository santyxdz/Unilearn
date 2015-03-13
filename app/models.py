#from app import db
from app import app
from flask.ext.social import Social
from flask.ext.social.datastore import SQLAlchemyConnectionDatastore

app.config['SECURITY_POST_LOGIN'] = '/profile'
#db = SQLAlchemy(app)
