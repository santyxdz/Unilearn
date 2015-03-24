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
api.add_resource(Error, '/api', "/api/")
api.add_resource(User, "/api/user/<username>")
api.add_resource(Topic, "/api/topic/<topic_name>")