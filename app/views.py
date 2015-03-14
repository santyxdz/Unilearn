# -*- coding: utf8 -*-
from flask import Flask
import flask
from flask import redirect,render_template
from flask_oauthlib.client import OAuth

from app import models, app, configs
from app import db


oauth = OAuth(app)
twitter = oauth.remote_app('twitter',
    base_url='https://api.twitter.com/1.1/',
    request_token_url='https://api.twitter.com/oauth/request_token',
    access_token_url='https://api.twitter.com/oauth/access_token',
    authorize_url='https://api.twitter.com/oauth/authenticate',
    consumer_key=configs.TW_APP_ID,
    consumer_secret=configs.TW_APP_SECRET,
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
    return flask.render_template('home.html')


@app.route("/register", methods=['POST', 'GET'])
def register():
    error = None
    if flask.request.method == "POST":
        users = models.User.query.filter_by(username=flask.request.form["username"].lower()).all()
        if len(users) > 0:
            return "ERROR: El Nombre de Usuario ya esta Registrado"
        else:
            user = models.User(flask.request.form["username"], flask.request.form["email"], flask.request.form["password"])
            db.session.add(user)
            db.session.commit()
            return flask.redirect(flask.url_for("home"))
    return flask.render_template("register.html")


@app.route("/users")
def users():
    users_list = models.User.query.all()
    return flask.render_template("users.html", users=users_list)


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
    return flask.render_template('404.html'), 404

@twitter.tokengetter
def get_twitter_token():
    if 'twitter_oauth' in flask.session:
        resp = flask.session['twitter_oauth']
        return resp['oauth_token'], resp['oauth_token_secret']


@app.before_request
def before_request():
    flask.g.user = None
    if 'twitter_oauth' in flask.session:
        flask.g.user = flask.session['twitter_oauth']

@app.route('/login')
def login():
    callback_url = flask.url_for('oauthorized', next=flask.request.args.get('next'))
    return twitter.authorize(callback=callback_url or flask.request.referrer or None)

@app.route('/logout')
def logout():
    flask.session.pop('twitter_oauth', None)
    return redirect(flask.url_for('index'))

@app.route('/oauthorized')
def oauthorized():
    resp = twitter.authorized_response()
    if resp is None:
        flask.flash('You denied the request to sign in')
    else:
        flask.session['twitter_oauth'] = resp
    return flask.redirect(flask.url_for('success'))

@app.route('/success')
def success():
    return flask.render_template("register.html")
