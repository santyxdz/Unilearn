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


class QuestionModel(db.Model):
    cod = db.Column(db.Integer,  primary_key=True)
    #area = db.Column(db.String(15), primary_key=True)
    statement = db.Column(db.Text)

    def __init__(self, cod, statement):
        self.cod = cod
        self.statement = statement
        print "Question: "+self.__repr__()

    def __repr__(self):
        return "<QuestionModel @"+self.cod

class Answers(db.Model):
    cod = db.Column(db.Integer, unique = True, primary_key = True)
    estado = db.Column(db.Booleand, unique = True)
    text= db.Column(db.Text)
    pregunta_cod = db.Column(db.Integer, db.ForeignKey('QuestionModel.cod'))
    pregunta = db.relationship('QuestionModel', backref=db.backref('answers', lazy='dynamic'))

    def __init__(self, cod, estado, text, pregunta):
        self.cod = cod
        self.estado = estado
        self.textR = text
        self.pregunta = pregunta

    def __repr__(self):
        return "Answers @"+self.cod


class QuestionSMU(QuestionModel):
    pass