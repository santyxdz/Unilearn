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


class Topic(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    name = db.Column(db.String(100))
    description = db.Column(db.Text)
    icon = db.Column(db.Text)
    #questions & quiestions.all()

    def __init__(self, name, description):
        self.name = name
        self.description = description
        print "New: "+self.__repr__()

    def __repr__(self):
        return "<Area @"+self.name+">"


class QuestionModel(db.Model):
    cod = db.Column(db.Integer,  primary_key=True, unique=True)
    statement = db.Column(db.Text)
    topic_cod = db.Column(db.Integer, db.ForeignKey('topic.id'))
    topic = db.relationship('Topic', backref=db.backref('questions'))
    #answers & answers.all()
    __mapper_args__ = {
        'polymorphic_on': None,
        'polymorphic_identity': 'question_model',
        'with_polymorphic': '*'
    }
    def __init__(self, statement, topic):
        self.statement = statement
        self.topic = topic
        print "Question: "+self.__repr__()

    def __repr__(self):
        return "<QuestionModel @"+self.statement

class Answers(db.Model):
    cod = db.Column(db.Integer, unique=True, primary_key=True)
    estado = db.Column(db.Boolean)
    text= db.Column(db.Text)
    pregunta_cod = db.Column(db.Integer, db.ForeignKey('question_model.cod'))
    pregunta = db.relationship('QuestionModel', backref=db.backref('answers', lazy='dynamic'))

    def __init__(self, estado, text, pregunta):
        self.estado = estado
        self.text = text
        self.pregunta = pregunta
        print "Answers: "+self.__repr__()

    def __repr__(self):
        return "Answers @"+self.text


class QuestionSMU(QuestionModel):
    __tablename__ = 'question_smu'
    id = db.Column(db.Integer, db.ForeignKey('question_model.cod'), primary_key=True)
    __mapper_args__ = {
        'polymorphic_identity': 'question_smu',
    }
    def ValidateAnswer(self, selection):
        if (selection.estado == True):
            """ aqui va la todo lo que tiene que ver con Gamificacion"""
            print "Respuesta Correcta"
        else:
            print "Respuesta Incorrecta"



class QuestionCompletation(QuestionModel):
    __tablename__ = 'question_completation'
    id = db.Column(db.Integer, db.ForeignKey('question_model.cod'), primary_key=True)
    __mapper_args__ = {
        'polymorphic_identity': 'question_completation',
    }
    def ValidateAnswer(self, selection, text):
        if (selection.text == str(text)):
            """ en este condicional creo que es mejor comparar el .tetx
            aqui va la todo lo que tiene que ver con Gamificacion """
            print "Respuesta Correcta"
        else:
            print "Respuesta Incorrecta"

class QuestionSMM(QuestionModel):
    __tablename__ = 'question_smm'
    id = db.Column(db.Integer, db.ForeignKey('question_model.cod'), primary_key=True)
    __mapper_args__ ={
        'polymorphic_identity': 'question_smm',
    }
    def ValidateAnswer(self, answerSaved, selection):
        cont=0
        for i in selection:
            if i.estado == True:
                cont +=1
        score = float((1.0/float(answerSaved))*cont - (1.0/float(answerSaved))*(len(selection)-cont))
        if (score >= 0):
            print cont," Respuesta(s) correctas",len(selection)-cont, "Respuesta(s) falsas"
            print "Puntaje: ", score
        else:
            print float(0.0)


