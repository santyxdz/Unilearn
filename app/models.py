from app import db
from app import app
from json import loads

app.config['SECURITY_POST_LOGIN'] = '/profile'


class User(db.Model):
    username = db.Column(db.String(15), unique=True, primary_key=True)
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(200))
    tw_username = db.Column(db.String(200))
    # fb_id = db.Column(db.String(250))
    # gl_username = db.Column(db.String(250))
    email = db.Column(db.String(300), unique=True)
    password = db.Column(db.String(300))
    photo = db.Column(db.Text)
    cur_topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'))  # Curso publico actual
    cur_topic = db.relationship("Topic")
    scores = db.relationship("UserScore", backref="topic", cascade='all, delete-orphan')
    life = db.Column(db.Integer)
    type = db.Column(db.String(50))  # Profesor | Estudiante
    # Cursos = Cursos ... por hacer

    def __init__(self, username, email, password, first_name="", last_name="", photo="", tw_un=""):
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password
        self.photo = photo
        self.tw_username = tw_un
        print "New User: " + self.__repr__()

    def score(self):
        return sum([x.score for x in self.scores])

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
    type = db.Column(db.String(50))
    statement = db.Column(db.Text)
    image = db.Column(db.Text)
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'))
    answers = db.relationship("Answer", backref="question", cascade='all, delete-orphan')
    users = db.relationship("UserScore", backref="question", cascade='all, delete-orphan')
    __mapper_args__ = {
        'polymorphic_on': type,
        'polymorphic_identity': 'question',
        'with_polymorphic': '*'
    }

    def __init__(self, statement, topic, image=""):
        self.statement = statement
        self.topic_id = topic
        self.image = image
        print "Question: " + self.__repr__()

    def __repr__(self):
        return "<Question @" + self.statement

    def set_image(self, image=""):
        if image:
            self.image = image

# Multiple Selection Unique Response
class MSUQuestion(Question):
    __tablename__ = 'msu_question'
    id = db.Column(db.Integer, db.ForeignKey('question.id'), primary_key=True)
    __mapper_args__ = {'polymorphic_identity': 'msu_question'}

    # @staticmethod
    def validate_answer(self, selected, true_one):
        if selected == true_one:
            return {"score": 1.0, "message": "Score! You've got 100% correct"}
        return {"score": 0.0, "message": "Ops! Incorrect! But for your trying you've got a 0,01%. Keep trying!"}

class CompletationQuestion(Question):
    __tablename__ = 'completation_question'
    id = db.Column(db.Integer, db.ForeignKey('question.id'), primary_key=True)
    __mapper_args__ = {'polymorphic_identity': 'completation_question'}

    def validate_answer(self, text):
        #if str(selection).decode('utf-8').lower() == str(text).decode('utf-8').lower():
        answers = [x.text.lower() for x in self.answers]
        if text.lower() in answers:
            return {"score": 1.0, "message": "Excelent, correct answer!"}
        else:
            return {"score": 0.0, "message": "Bad answer, try again"}


# Multiple Selection Multiple Response
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
            return {"score": score, "message": "You've got "+str(score*100)+"% correct"}
        else:
            return {"score": 0.0, "message": "You've lost, try it again"}


class ClasificationQuestion(Question):
    __tablename__ = 'clasification_question'
    id = db.Column(db.Integer, db.ForeignKey('question.id'), primary_key=True)
    __mapper_args__ = {'polymorphic_identity': 'clasification_question'}

    @staticmethod
    def validate_answer(answer_given, answer_stored):
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
        print "Punctuation = %d per cent correct!" % ((correct_ans / (correct_ans + incorrect_ans)) * 100)
        return {
            "score": ((correct_ans / (correct_ans + incorrect_ans)) * 100),
            "message": "This was your punctuation"
        }



class PairingQuestion(Question):
    __tablename__ = "pairing_question"
    id = db.Column(db.Integer, db.ForeignKey('question.id'), primary_key=True)
    __mapper_args__ = {'polymorphic_identity': 'question_smm'}

    def validate_answer(self, answer_given, answer_stored):
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
        print "Punctuation = %d per cent correct!" % ((correct_ans / (correct_ans + incorrect_ans)) * 100)
        return {
            "score": ((correct_ans / (correct_ans + incorrect_ans)) * 100),
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
