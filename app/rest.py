from flask_restful import Resource, Api
from flask import request
from app import api
from app import db
from app import views
from app import models
from flask_login import login_user, logout_user, current_user, login_required
import json

"""
todos = {}

class TodoSimple(Resource):
    def get(self, todo_id=""):
        if todos[todo_id] is None:
            return {"error": "Not Found"}
        return {todo_id: todos[todo_id]}

    def put(self, todo_id):
        if todo_id == "" or request.form['data'] is not None:
            return {"error": "Not Data found"}
        todos[todo_id] = request.form['data']
        return {todo_id: todos[todo_id]}
"""


class RError(Resource):
    def get(self):
        return {"error": "Not Accesible"}

    def put(self):
        return {"error": "Not Accesible"}


class RUser(Resource):
    def get(self, username):
        user = models.User.query.filter_by(username=username).first()
        if views.is_empty(user):
            return {
                "result": False,
                "status": "error",
                "error": "Username doesn't exit"
            }
        else:
            return {
                "result": True,
                "user": user.username,
                "status": "Successful, User is on DB"
            }

    def post(self, username):
        if "update" in request.form["method"]:
            return {"result": True}
        elif "create" in request.form["method"]:
            if self.get(username)["result"]:
                return {"error": "Username already exist"}
            else:
                user = models.User(username, request.form["email"], request.form["password"])
                db.session.add(user)
                db.session.commit()
                return {"status": "Successful, User Created"}
        else:
            return {"error": "What are you trying to do?"}


class RTopic(Resource):
    def get(self, topic_name):
        topic = models.Topic.query.filter_by(name=topic_name).first()
        if views.is_empty(topic):
            return {
                "result": False,
                "status": "error",
                "error": "Topic doesn't exit"
            }
        else:
            return {
                "result": True,
                "topic": topic.name,
                "status": "Successful, Topic is on DB"
            }

    def post(self, topic_name):
        if "update" in request.form["method"]:
            return {"result": True}
        elif "create" in request.form["method"]:
            if self.get(topic_name)["result"]:
                return {"error": "Topic already exist"}
            else:
                if "icon" in request.form:
                    topic = models.Topic(topic_name, request.form["description"], request.form["icon"])
                else:
                    topic = models.Topic(topic_name, request.form["description"])
                db.session.add(topic)
                db.session.commit()
                return {"status": "Successful, User Created"}
        else:
            return {"error": "What are you trying to do?"}


class RQuestion(Resource):
    def get(self, question_id=None):
        if question_id is None:
            questions = models.Question.query.all()
            return {
                "questions": [x.id for x in questions]
            }
        else:
            question = models.Question.query.filter_by(id=question_id).first()
            if views.is_empty(question):
                return {
                    "result": False,
                    "status": "error",
                    "error": "question not found"
                }
            else:
                return {
                    "result": True,
                    "type": question.type,
                    "topic": question.topic.name,
                    "status": "Successfull"
                }

    def post(self, question_id=None):
        if question_id is None:
            if "update" in request.form["method"]:
                return {"result": True}
            elif "create" in request.form["method"]:
                if "statement" in request.form and "topic" in request.form:  # and "type" in request.form:
                    type_specified = request.form["type"]
                    if type_specified == "msu":  # for multiple selection unique response questions
                        question = models.MSUQuestion(request.form["statement"], request.form["topic"])
                    elif type_specified == "msm":  # multiple selection multiple response
                        question = models.MSMQuestion(request.form["statement"], request.form["topic"])
                    elif type_specified == "completation":
                        question = models.CompletationQuestion(request.form["statement"], request.form["topic"])
                    elif type_specified == "clasification":
                        question = models.ClasificationQuestion(request.form["statement"], request.form["topic"])
                    elif type_specified == "pairing":
                        question = models.PairingQuestion(request.form["statement"], request.form["topic"])
                    else:
                        return {
                            "status": False,
                            "error": "type specified is not supported"
                        }
                    try:
                        question = models.Question(request.form["statement"], request.form["topic"])
                    except Exception:
                        return {
                            "status": False,
                            "message": Exception.message
                        }
                    # image = request.form["image"]
                    #if image is not None:
                    #    question.set_image(image)
                    db.session.add(question)
                    db.session.commit()
                    return {
                        "status": True,
                        "message": "Question creation successful"
                    }
                else:
                    return {
                        "status": False,
                        "type": "PANIC",
                        "error": "no statement or topic or type specified!"
                    }
            else:
                return {
                    "status": False,
                    "message": "method specified is not supported"
                }
        else:
            return {
                "status": False,
                "message": "can't create a specified question, do not tell me the id!"
            }


class RAnswer(Resource):
    def get(self, question_id, answer_id=None):
        if question_id and answer_id:
            try:
                answer = models.Answer.query.filter_by(id=answer_id, question_id=question_id).first()
                return {
                    "result": True,
                    "answer": answer.id,
                    "belongs to question": answer.question_id,
                    "state": answer.state
                }
            except Exception:
                return {
                    "status": False,
                    "error": Exception.message
                }
        elif question_id:
            try:
                answers = models.Answer.query.filter_by(question_id=question_id).all()
                question = models.Question.query.filter_by(id=question_id).first()
                return {
                    "status": True,
                    "question": question_id,
                    "statement": question.statement,
                    "answers": [ans.id for ans in answers]
                }
            except Exception:
                return {
                    "status": False,
                    "error": Exception.message
                }
        else:
            return {
                "status": False,
                "message": "question id or answer id not specified"
            }

    def post(self, question_id=None, answer_id=None):
        if question_id is not None or answer_id is not None:
            return {
                "status": False,
                "error": "This doesn't make sense..."
            }
        else:
            if "create" in request.form["method"]:
                if "text" in request.form and "state" in request.form and "question" in request.form:
                    if "image" in request.form:
                        answer = models.Answer(request.form["state"], request.form["text"], request.form["question"],
                                               request.form["image"])
                    else:
                        answer = models.Answer(request.form["state"], request.form["text"], request.form["question"])
                    db.session.add(answer)
                    db.commit()
                    return {
                        "status": True,
                        "message": "Answer created",
                        "question": "And it belongs to" + answer.question_id + "question"
                    }
                else:
                    return {
                        "status": False,
                        "message": "Missing information"
                    }
            else:
                return {
                    "status": False,
                    "message": "method specified is not supported"
                }


class REvaluate(Resource):
    # ASI SE HACE EN JAVASCRIPT-jQuery PARA El Post los datos son el dicionario despues de la url
    #En fin la cosa es que como se los enviabamos en postman es viable por rest, las listas
    #tambien se pueden enviar si tienen el mismo nombre y otra cosa ahi.
    #Si algo vean el jquery.json
    #No terminado pueden sergirlo la cosa es que se envie a /evaluate/<int:question>
    #y esto le devuelva cuando saco (flatante) y como devuelve json se pueden poner mas cosas
    # $.post("/api/question/",{method:"update"},function(data){console.log(data.result)},"json");
    def post(self, question_id=None):
        if question_id is None:
            return {"error": "Not accessible",
                    "result": False
                    }
        else:
            question = models.Question.query.filter_by(id=question_id).first()
            user = models.User.query.filter_by(username=current_user.username).first()
            if question is None:
                return {"error": "Question not found",
                        "result": False
                        }
            else:
                if "type" in request.form and "selected" in request.form:
                    if request.form["type"] == "msu":
                        trueOne = [x.id for x in question.answers if x.state]
                        selected = json.loads(request.form["selected"])
                        result = question.validate_answer(selected[0], trueOne[0])
                        result["points"] = result["score"]*question.max_score
                        views.new_question(current_user.username, question, result["points"])
                        if result["score"] == 0.0:
                            user.remove_life()
                            db.session.commit()
                        if result["score"] == 1.0:
                            user.give_life()
                            db.session.commit()
                        return result
                    if request.form["type"] == "msm":
                        trueOne = [x.id for x in question.answers if x.state]
                        selected = json.loads(request.form["selected"])
                        selected_objects = [models.Answer.query.filter_by(id=x).first() for x in selected]
                        result = question.validate_answer(len(trueOne), selected_objects)
                        result["points"] = int(result["score"]*question.max_score)
                        views.new_question(current_user.username, question, result["points"])
                        if result["score"] == 0.0:
                            user.remove_life()
                            db.session.commit()
                        if result["score"] == 1.0:
                            user.give_life()
                            db.session.commit()
                        return result
                    if request.form["type"] == "completation":
                        selected = json.loads(request.form["selected"])
                        result = question.validate_answer(selected[0])
                        result["points"] = result["score"]*question.max_score
                        views.new_question(current_user.username, question, result["points"])
                        if result["score"] == 0.0:
                            user.remove_life()
                            db.session.commit()
                        if result["score"] == 1.0:
                            user.give_life()
                            db.session.commit()
                        return result
                    if request.form["type"] == "pairing":
                        # Se debe mandar la respuesta en formato JSON.
                        correct = [x.id for x in question.answers if x.state]
                        result = question.validate_answer(request.form["answer_given"], correct[0])
                        result["points"] = result["score"]*question.max_score
                        return result
                    if request.form["type"] == "clasification":
                        correct = [ans.id for ans in question.answers if ans.state]
                        result = question.validate_answer(request.form["answer_given"], correct[0])
                        result["points"] = result["score"]*question.max_score
                        return result
                    else:
                        return {
                            "error": "Type Invalid",
                            "result": False
                        }


class RRegister(Resource):
    def post(self):
        if "user" in request.form and "topic_id" in request.form:
            cur_user = models.User.query.filter_by(username=request.form["user"]).first()
            topic = models.Topic.query.filter_by(id=int(request.form["topic_id"])).first()
            if cur_user is None and topic is None:
                return{
                    "status": False,
                    "message": "User and Topic don't exist"
                }
            elif cur_user is None:
                return {
                    "status": False,
                    "message": "User not found"
                }
            elif topic is None:
                return {
                    "status": False,
                    "message": "Topic not found"
                }
            cur_user.set_topic(request.form["topic_id"])
            db.session.commit()
            return {
                "status": True,
                "message": "User registered successfully"
            }
        else:
            return {
                "status": False,
                "message": "Operation un-supported"
            }

    def get(self, username):
        user = models.User.query.filter_by(username=username).first()
        if views.is_empty(user):
            return {
                "result": False,
                "status": "error",
                "error": "Username doesn't exit"
            }
        else:
            topic = models.Topic.query.filter_by(id=user.cur_topic_id).first()
            if views.is_empty(topic):
                return{
                    "result": False,
                    "message": "User is not inscribed in any topic"
                }
            else:
                return {
                    "result": True,
                    "topic": topic.name,
                    "status": "User has a Topic"
                }



api.add_resource(RError, '/api', "/api/")
api.add_resource(RUser, "/api/users/<username>")
api.add_resource(RTopic, "/api/topics/<topic_name>")
api.add_resource(RQuestion, "/api/question/<int:question_id>", "/api/question/")
api.add_resource(RAnswer, "/api/answer/<int:question_id>", "/api/answer/",
                 "/api/answer/<int:question_id>/<int:answer_id>")
api.add_resource(REvaluate, "/api/evaluate/", "/api/evaluate/<question_id>")
api.add_resource(RRegister, "/api/register/", "/api/register/<username>")
