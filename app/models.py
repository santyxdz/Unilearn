from app import db
from app import app


class Team(db.Model):
    username = db.Column(db.String(140), unique=True, primary_key=True)
    age = db.Column(db.Integer)

    def __init__(self, user, age):
        self.username = user
        self.age = age
        print "New User: "+self.__repr__()

    def __repr__(self):
        return '<Team %r>' % self.username