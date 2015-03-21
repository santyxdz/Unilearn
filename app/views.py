# -*- coding: utf8 -*-
from flask import Flask, g, url_for, request, render_template, flash, json, session
import flask
from flask import redirect, render_template
from flask_oauthlib.client import OAuth, OAuthException

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
facebook = oauth.remote_app('facebook',
                            base_url='http://graph.facebook.com/',
                            request_token_url=None,
                            access_token_url=configs.fb['acces_token_url'],
                            authorize_url=configs.fb['authorize_url'],
                            consumer_key=configs.fb['id'],
                            consumer_secret=configs.fb['secret'],
                            request_token_params={'scope': 'email'}
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


@app.route('/login/tw')
def tw_login():
    callback_url = url_for('oauthorized', next=request.args.get('next'))
    return twitter.authorize(callback=callback_url or request.referrer or None)


@app.route('/login/fb')
def fb_login():
    callback = url_for('facebook_authorized', next=request.args.get('next') or request.referrer or None,
                       _external=True)
    return facebook.authorize(callback=callback)


@app.route('/login/fb/authorized')
def facebook_authorized():
    resp = facebook.authorized_response()
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    if isinstance(resp, OAuthException):
        return 'Access denied %s' % resp.message

    session['oauth_token'] = (resp['access_token'], '')
    me = facebook.get('/me')
    return 'logged in as id=%s name=%s redirect=%s' % (
        me.data['id'], me.data['name'], request.args.get('next')
    )


@facebook.tokengetter
def get_facebook_oauth_token():
    return session.get('oauth_token')


@app.route('/logout')
def logout():
    #try:
    #    session.pop('twitter_oauth', None)
    #    session.pop("user")
    session.clear()
    #except KeyError:
    #    pass
    return redirect(url_for("login"))


@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == "POST":
        user = models.User.query.filter_by(username=request.form["username"]).first()
        if is_empty(user):
            return "Usuario no encontrado"
        else:
            if user.password == request.form["password"]:
                session["user"] = user.username
                return redirect(url_for("home"))
            else:
                return "Contraseña incorrecta"

    return render_template("login.html")


@app.route("/forgot_password")
def forgot_password():
    return render_template("login.html")


@app.route('/oauthorized')
def oauthorized():
    resp = twitter.authorized_response()
    if resp is None:
        flash('You denied the request to sign in')
    else:
        session['twitter_oauth'] = resp
    return render_template("register.html", username=resp['screen_name'])
