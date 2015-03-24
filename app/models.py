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
    __tablename__ = "topic"
    id = db.Column(db.Integer, primary_key=True, unique=True)
    name = db.Column(db.String(100), unique=True)
    description = db.Column(db.Text)
    icon = db.Column(db.Text)
    questions = db.relationship("Question", backref="topic", cascade='all, delete-orphan')

    def __init__(self, name, description, icon=""):
        self.name = name
        self.description = description
        self.icon = icon
        print "New: " + self.__repr__()

    def __repr__(self):
        return "<Area @" + self.name + ">"


class Question(db.Model):
    __tablename__ = 'question'
    id = db.Column(db.Integer,  primary_key=True, unique=True)
    type = db.Column(db.String(20))
    statement = db.Column(db.Text)
    image = db.Column(db.Text)
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'))
    answers = db.relationship("Answer", backref="question", cascade='all, delete-orphan')
    __mapper_args__ = {
        'polymorphic_on': type,
        'polymorphic_identity': 'question',
        'with_polymorphic': '*'
    }

    def __init__(self, statement, topic, image=""):
        self.statement = statement
        self.topic_id = topic
        self.image = image
        print "Question: "+self.__repr__()

    def __repr__(self):
        return "<Question @" + self.statement



class MSUQuestion(Question):
    __tablename__ = 'msu_question'
    id = db.Column(db.Integer, db.ForeignKey('question.id'), primary_key=True)
    __mapper_args__ = {'polymorphic_identity': 'msu_question'}

   # @staticmethod
    def validate_answer(selection):
        if selection.state == True:
            """ aqui va la todo lo que tiene que ver con Gamificacion"""
            print "Respuesta Correcta"
        else:
            print "Respuesta Incorrecta"

class CompletationQuestion(Question):
    __tablename__ = 'completation_question'
    id = db.Column(db.Integer, db.ForeignKey('question.id'), primary_key=True)
    __mapper_args__ = {'polymorphic_identity': 'completation_question'}

    def ValidateAnswer(self, selection, text):
        if (selection.text == str(text)):
            """ en este condicional creo que es mejor comparar el .tetx
            aqui va la todo lo que tiene que ver con Gamificacion """
            print "Respuesta Correcta"
        else:
            print "Respuesta Incorrecta"


class MSMQuestion(Question):
    __tablename__ = 'msm_question'
    id = db.Column(db.Integer, db.ForeignKey('question.id'), primary_key=True)
    __mapper_args__ = {'polymorphic_identity': 'msm_question'}

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

class ClasificationQuestion(Question):
    __tablename__ = 'clasification_question'
    id = db.Column(db.Integer, db.ForeignKey('question.id'), primary_key=True)
    __mapper_args__ = {'polymorphic_identity': 'clasification_question'}

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

class PairingQuestion(Question):
    __tablename__ = "pairing_question"
    id = db.Column(db.Integer, db.ForeignKey('question.id'), primary_key=True)
    __mapper_args__ ={'polymorphic_identity': 'question_smm'}

    def ValidateAnswer(self, answers, selected):
        #items = answers.keys()
        pass

class Answer(db.Model):
    id = db.Column(db.Integer, unique=True, primary_key=True)
    state = db.Column(db.Boolean)
    text = db.Column(db.Text)
    image = db.Column(db.Text)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))

    def __init__(self, state, text, question, image=""):
        self.state = state
        self.text = text
        self.question_id = question
        self.image = image
        print "Answers: "+self.__repr__()

    def __repr__(self):
        return "Answers @" + self.text
