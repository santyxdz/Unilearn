from app import db
from app import app
from json import loads

app.config['SECURITY_POST_LOGIN'] = '/profile'


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
        print "New User: " + self.__repr__()

    def __repr__(self):
        return "<User @" + self.username + ">"


class Topic(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    name = db.Column(db.String(100), unique=True)
    description = db.Column(db.Text)
    icon = db.Column(db.Text)
    # questions & quiestions.all()

    def __init__(self, name, description, icon=""):
        self.name = name
        self.description = description
        self.icon = icon
        print "New: " + self.__repr__()

    def __repr__(self):
        return "<Area @" + self.name + ">"


class QuestionModel(db.Model):

    __tablename__ = 'question_model'
    cod = db.Column(db.Integer,  primary_key=True, unique=True)
    statement = db.Column(db.Text)
    image = db.Column(db.Text)
    topic_cod = db.Column(db.Integer, db.ForeignKey('topic.id'))
    topic = db.relationship('Topic', backref=db.backref('questions'))
    # answers & answers.all()
    __mapper_args__ = {
        'polymorphic_on': None,
        'polymorphic_identity': 'question_model',
        'with_polymorphic': '*'
    }
    def __init__(self, statement, topic, image=""):
        self.statement = statement
        self.topic = topic
        self.image = image
        print "Question: "+self.__repr__()

    def __repr__(self):
        return "<QuestionModel @" + self.statement


class Answers(db.Model):
    cod = db.Column(db.Integer, unique=True, primary_key=True)
    state = db.Column(db.Boolean)
    text = db.Column(db.Text)
    image = db.Column(db.Text)
    question_cod = db.Column(db.Integer, db.ForeignKey('question_model.cod'))
    question = db.relationship('QuestionModel', backref=db.backref('answers', lazy='dynamic'))

    def __init__(self, state, text, question, image=""):
        self.state = state
        self.text = text
        self.question = question
        self.image = image
        print "Answers: "+self.__repr__()

    def __repr__(self):
        return "Answers @" + self.text


class MSUQuestion(QuestionModel):
    __tablename__ = 'msu_question'
    id = db.Column(db.Integer, db.ForeignKey('question_model.cod'), primary_key=True)
    __mapper_args__ = {
        'polymorphic_identity': 'msu_question',
    }

    def ValidateAnswer(self, selection):
        if (selection.state == True):
            """ aqui va la todo lo que tiene que ver con Gamificacion"""
            print "Respuesta Correcta"
        else:
            print "Respuesta Incorrecta"

class CompletationQuestion(QuestionModel):
    __tablename__ = 'completation_question'
    id = db.Column(db.Integer, db.ForeignKey('question_model.cod'), primary_key=True)
    __mapper_args__ = {
        'polymorphic_identity': 'completation_question',
    }

    def ValidateAnswer(self, selection, text):
        if (selection.text == str(text)):
            """ en este condicional creo que es mejor comparar el .tetx
            aqui va la todo lo que tiene que ver con Gamificacion """
            print "Respuesta Correcta"
        else:
            print "Respuesta Incorrecta"


class MSMQuestion(QuestionModel):
    __tablename__ = 'msm_question'
    id = db.Column(db.Integer, db.ForeignKey('question_model.cod'), primary_key=True)
    __mapper_args__ ={
        'polymorphic_identity': 'msm_question',
    }

    def ValidateAnswer(self, answerSaved, selection):
        cont = 0
        for i in selection:
            if i.state == True:
                cont +=1
        score = float((1.0/float(answerSaved))*cont - (1.0/float(answerSaved))*(len(selection)-cont))
        if (score >= 0):
            print cont, " Respuesta(s) correctas", len(selection) - cont, "Respuesta(s) falsas"
            print "Puntaje: ", score
        else:
            print float(0.0)

class ClasificationQuestion(QuestionModel):
    __tablename__ = 'clasification_question'
    id = db.Column(db.Integer, db.ForeignKey('question_model.cod'), primary_key=True)
    __mapper_args__ = {
        'polymorphic_identity': 'clasificarion_question',
    }

    def ValidateAnswer(self, answer_given, answer_stored):
        user_ans_dict = loads(answer_given)
        correct_dict = loads(answer_stored)
        keys = answer_given.keys()
        correct_ans = 0
        incorrect_ans = 0
        for key in keys:
            if user_ans_dict[key] == correct_dict[key]:
                correct_ans += 1
            else:
                incorrect_ans += 1
        print "You've got %d correct matches and %d incorrect ones" % (correct_ans, incorrect_ans)
        print "Punctuation = %d per cent correct!" % ((correct_ans/(correct_ans+incorrect_ans))*100)

class PairingQuestion(QuestionModel):
    __tablename__ = "pairing_question"
    id = db.Column(db.Integer, db.ForeignKey('question_model.cod'), primary_key=True)
    __mapper_args__ ={
        'polymorphic_identity': 'question_smm',
    }

    def ValidateAnswer(self, answers, selected):
        #items = answers.keys()
        pass
