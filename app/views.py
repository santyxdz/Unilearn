# -*- coding: utf8 -*-
from flask import Flask, g, url_for, request,render_template, flash, json, session
import flask
from flask import redirect, render_template
from flask_oauthlib.client import OAuth

from app import models, app, configs
from app import db


oauth = OAuth(app)
twitter = oauth.remote_app('twitter',
                           base_url=configs.tw['base_url'],
                           request_token_url=configs.tw['request_token_url'],
                           access_token_url=configs.tw['access_token_url'],
                           authorize_url=configs.tw['authorize_utl'],
                           consumer_key=configs.tw['ID'],
                           consumer_secret=configs.tw['SECRET']
                           )


@app.template_global()
def is_empty(item):
    if isinstance(item, type(None)):
        return True
    elif item == "":
        return True
    return False


@app.route("/main")
@app.route('/index')
@app.route('/')
def home():
    return render_template('home.html')


@app.route("/register", methods=['POST', 'GET'])
def register():
    error = None
    if request.method == "POST":
        users = models.User.query.filter_by(username=flask.request.form["username"].lower()).all()
        if len(users) > 0:
            return "ERROR: El Nombre de Usuario ya esta Registrado"
        else:
            user = models.User(request.form["username"], request.form["email"],
                               request.form["password"])
            db.session.add(user)
            db.session.commit()
            return redirect(flask.url_for("home"))
    return render_template("register.html")


@app.route("/users")
def users():
    users_list = models.User.query.all()
    return render_template("users.html", users=users_list)


@app.route("/courses")
def courses():
    return render_template("courses.html", courses=models.Topic.query.all())


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


@twitter.tokengetter
def get_twitter_token():
    if 'twitter_oauth' in session:
        resp = session['twitter_oauth']
        return resp['oauth_token'], resp['oauth_token_secret']


@app.before_request
def before_request():
    g.user = None
    if 'twitter_oauth' in session:
        g.user = session['twitter_oauth']


@app.route('/login')
def login():
    callback_url = url_for('oauthorized', next=request.args.get('next'))
    return twitter.authorize(callback=callback_url or request.referrer or None)


@app.route('/logout')
def logout():
    session.pop('twitter_oauth', None)
    return redirect(url_for('index'))


@app.route('/oauthorized')
def oauthorized():
    resp = twitter.authorized_response()
    if resp is None:
        flash('You denied the request to sign in')
    else:
        session['twitter_oauth'] = resp
    return redirect(url_for('yeah'))


@app.route('/auth')
def yeah():
    resp = twitter.get('account/verify_credentials.json')
    #user = json.load(resp.data)
    #BETA
    if resp.status == 200:
        flash(resp.data)
    return render_template("login.html")
