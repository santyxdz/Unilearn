from flask_restful import Resource, Api
from flask import request
from app import api
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
class Error(Resource):
    def get(self):
        return {"error": "Not Accesible"}
    def put(self):
        return {"error": "Not Accesible"}
api.add_resource(TodoSimple, '/api/<string:todo_id>')
api.add_resource(Error, '/api', "/api/")