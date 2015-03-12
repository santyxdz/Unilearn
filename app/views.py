# -*- coding: utf8 -*-
from flask import render_template, redirect, session, url_for, request, json
from app import models, app, db, rest

@app.route("/main")
@app.route('/index')
@app.route('/')
def home():
    return render_template('home.html')


@app.route("/register", methods=['POST', 'GET'])
def register():
    error = None
    if request.method == "POST":
        users = models.User.query.filter_by(username=request.form["username"].lower()).all()
        if len(users) > 0:
            return "ERROR: El Nombre de Usuario ya esta Registrado"
        else:
            user = models.User(request.form["username"], request.form["email"], request.form["password"])
            db.session.add(user)
            db.session.commit()
            return redirect(url_for("home"))
    return render_template("register.html")


@app.route("/users")
def users():
    users_list = models.User.query.all()
    return render_template("users.html", users=users_list)


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=600'
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404