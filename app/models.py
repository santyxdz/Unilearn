from app import db
from app import app
from json import loads
from flask_login import UserMixin

app.config['SECURITY_POST_LOGIN'] = '/profile'


class User(UserMixin, db.Model):
    username = db.Column(db.String(15), unique=True, primary_key=True)
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(200))
    social_id = db.Column(db.String(100), unique=True)
    email = db.Column(db.String(300), unique=True)
    password = db.Column(db.String(300))
    photo = db.Column(db.Text)
    cur_topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'))  # Curso publico actual
    cur_topic = db.relationship("Topic")
    scores = db.relationship("UserScore", backref="user", cascade='all, delete-orphan')
    helpreport = db.relationship("HelpReport", backref="user", cascade='all, delete-orphan')
    life = db.Column(db.Integer)
    type = db.Column(db.String(50))  # Profesor | Estudiante
    # level = db.Column(db.Integer) # el topic que puede tomar despues de haber hecho el test de nivelacion
    # Cursos = Cursos ... por hacer

    def __init__(self, username, email, password, first_name="", last_name="", photo="", tw_un=""):
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password
        self.photo = photo
        self.tw_username = tw_un
        self.type = "student"
        # self.cur_topic_id = 1
        # self.level = 1
        print "New User: " + self.__repr__()

    def score(self):
        return sum([x.score for x in self.scores])

    def set_topic(self, topic_id):
        self.cur_topic_id = topic_id

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.username

    def __repr__(self):
        return "<User @" + self.username + ">"

    def remove_life(self):
        if self.life > 0:
            self.life -= 1

    def give_life(self):
        if self.life < 10:
            self.life += 1

class Topic(db.Model):
    __tablename__ = "topic"
    id = db.Column(db.Integer, primary_key=True, unique=True)
    name = db.Column(db.String(100), unique=True)
    description = db.Column(db.Text)
    icon = db.Column(db.Text)
    questions = db.relationship("Question", backref="topic", cascade='all, delete-orphan')
    helptheory = db.relationship("HelpTheory", backref="topic", cascade='all, delete-orphan')
    helpequation = db.relationship("HelpEquations", backref="topic", cascade='all, delete-orphan')


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
    type = db.Column(db.String(50))
    statement = db.Column(db.Text)
    image = db.Column(db.Text)
    max_score = db.Column(db.Integer)
    title = db.Column(db.String(70))
    #icon = db.Column(db.Text)
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'))
    answers = db.relationship("Answer", backref="question", cascade='all, delete-orphan')
    users = db.relationship("UserScore", backref="question", cascade='all, delete-orphan')
    helpvideo = db.relationship("HelpVideos", backref="question", cascade='all, delete-orphan')
    helpreport = db.relationship("HelpReport", backref="question", cascade='all, delete-orphan')
    __mapper_args__ = {
        'polymorphic_on': type,
        'polymorphic_identity': 'question',
        'with_polymorphic': '*'
    }

    def __init__(self, title, statement, topic, max_score, image=""):
        self.title = title
        self.statement = statement
        self.topic_id = topic
        self.image = image
        self.max_score = max_score
        print "Question: " + self.__repr__()

    def __repr__(self):
        return "<Question @" + self.statement

class MSUQuestion(Question):
    __tablename__ = 'msu_question'
    id = db.Column(db.Integer, db.ForeignKey('question.id'), primary_key=True)
    __mapper_args__ = {'polymorphic_identity': 'msu_question'}

    # @staticmethod
    def validate_answer(self, selected, true_one):
        if selected == true_one:
            return {"score": 1.0, "message": "FELICITACIONES"}
        else:
            return {"score": 0.0, "message": "INTENTA DE NUEVO"}

class CompletationQuestion(Question):
    __tablename__ = 'completation_question'
    id = db.Column(db.Integer, db.ForeignKey('question.id'), primary_key=True)
    __mapper_args__ = {'polymorphic_identity': 'completation_question'}

    def validate_answer(self, text):
        #if str(selection).decode('utf-8').lower() == str(text).decode('utf-8').lower():
        answers = [x.text.lower() for x in self.answers]
        if text.lower() in answers:
            return {"score": 1.0, "message": "FELICITACIONES"}
        else:
            return {"score": 0.0, "message": "INTENTA DE NUEVO"}

class MSMQuestion(Question):
    __tablename__ = 'msm_question'
    id = db.Column(db.Integer, db.ForeignKey('question.id'), primary_key=True)
    __mapper_args__ = {'polymorphic_identity': 'msm_question'}

    def validate_answer(self, answerSaved, selection):
        cont = 0
        for i in selection:
            if i.state:
                cont += 1
        score = float((1.0 / float(answerSaved)) * cont - (1.0 / float(answerSaved)) * (len(selection) - cont))
        if score >= 0:
            return {"score": score, "message": "OBTUVISTE "+str(score*100)+"% CORRECTO"}
        else:
            return {"score": 0.0, "message": "INTENTA DE NUEVO"}

class ClasificationQuestion(Question):
    __tablename__ = 'clasification_question'
    id = db.Column(db.Integer, db.ForeignKey('question.id'), primary_key=True)
    __mapper_args__ = {'polymorphic_identity': 'clasification_question'}

    def validate_answer(self, answer_given, answer_stored):
        user_ans_dict = loads(answer_given)
        correct_dict = loads(answer_stored)
        keys = user_ans_dict.keys()
        correct_ans = 0
        incorrect_ans = 0
        for key in keys:
            if user_ans_dict[key] == correct_dict[key]:
                correct_ans += 1
            else:
                incorrect_ans += 1
        return {
            "score": ((float(correct_ans) / (float(correct_ans) + float(incorrect_ans)))),
            "message": "This was your punctuation"
        }

class PairingQuestion(Question):
    __tablename__ = "pairing_question"
    id = db.Column(db.Integer, db.ForeignKey('question.id'), primary_key=True)
    __mapper_args__ = {'polymorphic_identity': 'question_smm'}

    def validate_answer(self, answer_given, answer_stored):
        user_ans_dict = loads(answer_given)
        correct_dict = loads(answer_stored)
        keys = user_ans_dict.keys()
        correct_ans = 0
        incorrect_ans = 0
        for key in keys:
            if user_ans_dict[key] == correct_dict[key]:
                correct_ans += 1
            else:
                incorrect_ans += 1
        return {
            "score": ((float(correct_ans) / (float(correct_ans) + float(incorrect_ans)))),
            "message": "This was your punctuation"
        }

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
        print "Answers: " + self.__repr__()

    def __repr__(self):
        return "Answers @" + self.text

class UserScore(db.Model):
    __tablename__ = "userscore"
    id = db.Column(db.Integer, unique=True, primary_key=True)
    user_username = db.Column(db.String(15), db.ForeignKey('user.username'))
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))
    score = db.Column(db.Integer)

    def __init__(self, user, question, score):
        self.user = user
        self.question = question
        self.score = score

    def __repr__(self):
        return "Score @" + self.score

class HelpTheory(db.Model):
    __tablename__ = "helptheory"
    id = db.Column(db.Integer, unique=True, primary_key=True)
    statement = db.Column(db.Text)
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'))

    def __init__(self, statement, topic):
        self.statement = statement
        self.topic = topic

    def __repr__(self):
        return "HelpTheory @" + self.topic

class HelpEquations(db.Model):
    __tablename__ = "helpequations"
    id = db.Column(db.Integer, unique = True, primary_key=True)
    equation = db.Column(db.Text)
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'))

    def __init__(self, equation, topic):
        self.equation = equation
        self.topic = topic

    def __repr__(self):
        return "HelpEquation @" + self.equation

class HelpVideos(db.Model):
    __tablename__= "helpvideos"
    id = db.Column(db.Integer, unique=True, primary_key=True)
    video_url = db.Column(db.Text) # aqui se guarda el link
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))

    def __init__(self, video, question):
        self.video_url = video
        self.question = question

    def __repr__(self):
        return "HelpVideo (link) @" + self.video

class HelpReport(db.Model):
    __tablename__= "helpreport"
    id = db.Column(db.Integer, unique=True, primary_key=True)
    report = db.Column(db.Text)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))
    user_username = db.Column(db.String(15), db.ForeignKey('user.username'))

    def __init__(self, report, question, user):
        self.report = report
        self.question = question
        self.user = user

    def __repr__(self):
        return "HelpReport @" + self.report
