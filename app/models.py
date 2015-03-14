from app import db
from app import app

app.config['SECURITY_POST_LOGIN'] = '/profile'



class Team(db.Model):
    username = db.Column(db.String(140), unique=True, primary_key=True)
    age = db.Column(db.Integer)

    def __init__(self, user, age):
        self.username = user
        self.age = age
        print "New User: "+self.__repr__()

    def __repr__(self):
        return '<Team %r>' % self.username


class User(db.Model):
    username = db.Column(db.String(15), unique=True, primary_key=True)
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(200))
    email = db.Column(db.String(300), unique=True)
    password = db.Column(db.String(300))
    photo = db.Column(db.Text)

    def __init__(self, username, email, password, first_name="", last_name="", photo=""):
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password
        self.photo = photo
        print "New User: "+self.__repr__()

    def __repr__(self):
        return "<User @"+self.username+">"

