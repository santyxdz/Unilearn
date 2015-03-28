# -*- coding: utf8 -*-
from flask import Flask, g, url_for, request, render_template, flash, json, session
import flask
from flask import redirect, render_template, abort
from flask_oauthlib.client import OAuth, OAuthException
import requests
from app import models, app, configs
from app import db
import encodings

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

@app.template_global()
def to_dic(item):
    return json.loads(item)

@app.template_global()
def no_repeated(item):
    return list(set(item))


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

@app.route("/courses/<course>")
def course(course):
    return render_template("course.html", course=models.Topic.query.filter_by(name=course).first())

@app.route("/courses/<course>/q/<int:num>")
def questions(course, num):
    topic = models.Topic.query.filter_by(name=course.encode('utf-8')).first()
    question = models.Question.query.filter_by(id=num, topic=topic).first()
    return render_template("question.html", question=question)


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

# Twitter Stuff!
# ******************************

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

@app.route('/login/tw/authorized')
def oauthorized():
    resp = twitter.authorized_response()
    if resp is None:
        flash('You denied the request to sign in')
    else:
        session['twitter_oauth'] = resp
    return render_template("register.html", username=resp['screen_name'])

# FB Stuff!
# *************************************

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

# Log-in with forms!
# *******************************************

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        user = models.User.query.filter_by(username=request.form["username"]).first()
        if is_empty(user):
            error = 'Invalid username'
        elif request.form['password'] != user.password:
            error = 'Invalid password'
        else:
            session['logged'] = True
            session['user'] = user.username
            flash('You were logged in')
            return redirect(url_for('home'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged', None)
    session.pop('user', None)
    flash('You were logged out')
    return redirect(url_for('home', reload=True))


@app.route("/forgot_password")
def forgot_password():
    return render_template("login.html")

# Question validation and sending
# ***********************
@app.route('/create/question/clasification', methods=['POST'])
def create_clasf():
    requests.post("http://localhost:5000/api/question", None ) # the recieved JSON must be sended here.
    return render_template("courses.html")
