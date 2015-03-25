from flask_restful import Resource, Api
from flask import request
from app import api
from app import db
from app import views
from app import models
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


class Error(Resource):
    def get(self):
        return {"error": "Not Accesible"}

    def put(self):
        return {"error": "Not Accesible"}


class User(Resource):
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


class Topic(Resource):
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
                return {"error": "Username already exist"}
            else:
                topic = models.Topic(topic_name, request.form["description"], request.form["icon"])
                db.session.add(topic)
                db.session.commit()
                return {"status": "Successful, User Created"}
        else:
            return {"error": "What are you trying to do?"}

class Question(Resource):
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
                if "statement" in request.form and "topic" in request.form:
                    if "image" in request.form:
                        question = models.Question(request.form["statement"], request.form["topic"], request.form["image"])
                    else:
                        question = models.Question(request.form["statement"], request.form["topic"])
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
                        "error": "no statement or topic specified!"
                    }
        else:
            return {
                "status": False,
                "error": "What the hell are you trying to do????"
            }


api.add_resource(Error, '/api', "/api/")
api.add_resource(User, "/api/users/<username>")
api.add_resource(Topic, "/api/topics/<topic_name>")
api.add_resource(Question, "/api/question/<int:question_id>", "/api/question/")