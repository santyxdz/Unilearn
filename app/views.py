# -*- coding: utf8 -*-
from flask import Flask, g, url_for, request, render_template, flash, json, session
import flask
from flask import redirect, render_template, abort
from flask_login import login_user, logout_user, current_user, login_required
from flask_oauthlib.client import OAuth, OAuthException
import requests
from app import models, app, configs, login_manager
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
    base_url='https://graph.facebook.com/',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth',
    consumer_key=configs.fb['id'],
    consumer_secret=configs.fb['secret'],
    request_token_params={'scope': 'email'}
)


from flask import make_response
from functools import wraps, update_wrapper
from datetime import datetime

def json_results(question):
    result = {}
    for x in question.answers:
        result.update(json.loads(x.text))
    return json.dumps(result)


def nocache(view):
    @wraps(view)
    def no_cache(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers['Last-Modified'] = datetime.now()
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        return response

    return update_wrapper(no_cache, view)


@app.template_global()
def is_empty(item):
    if isinstance(item, type(None)):
        return True
    elif item == "":
        return True
    return False


@app.template_global()
def set_default(item, replacement):
    if is_empty(item):
        return replacement
    else:
        return item

@app.template_global()
def to_dic(item):
    return json.loads(item)


@app.template_global()
def no_repeated(item):
    return list(set(item))

@app.template_global()
def question_made(user, question):
    userscore = models.UserScore.query.filter_by(user_username=user, question_id=question.id).first()
    if userscore:
        return userscore.score
@app.template_global()
def sort_topic(topic):
    topic.questions.sort(key=lambda x: x.id)
    return ""


def new_question(username, question, score):
        user = models.User.query.filter_by(username=username).first()
        previousScore = models.UserScore.query.filter_by(user_username=username, question_id=question.id).first()
        if isinstance(previousScore, type(None)):
                    userscore = models.UserScore(user, question, score)
                    db.session.add(userscore)
                    db.session.commit()
        else:
            if score > previousScore.score:
                previousScore.score = score
                db.session.commit()



@login_manager.user_loader
def load_user(user):
    return models.User.query.get(user)



@app.route("/main")
@app.route('/index')
@app.route('/')
@nocache
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
            if request.form["tw_username"]:
                user = models.User(request.form["username"], request.form["email"],
                               request.form["password"], tw_un=request.form["tw_username"])
            else:
                user = models.User(request.form["username"], request.form["email"],
                               request.form["password"])
            user.life = 10
            db.session.add(user)
            db.session.commit()
            return redirect(flask.url_for("home"))
    return render_template("register.html")


@app.route("/users")
@nocache
def users():
    users_list = models.User.query.all()
    return render_template("users.html", users=users_list)


@app.route("/courses")
@nocache
def courses():
    if current_user.is_authenticated():
        inscribed = models.Topic.query.filter_by(id=current_user.cur_topic_id).first()
        if inscribed is not None:
            return render_template("courses.html", courses=models.Topic.query.order_by(models.Topic.id).all(), active_topic=inscribed.name)
    return render_template("courses.html", courses=models.Topic.query.order_by(models.Topic.id).all())

@app.route("/courses/<course>")
@nocache
def course(course):
    return render_template("course.html", course=models.Topic.query.filter_by(name=course).first())

@app.route("/courses/<course>/q/<int:num>")
@nocache
def questions(course, num):
    topic = models.Topic.query.filter_by(name=course.encode('utf-8')).first()
    question = models.Question.query.filter_by(id=num, topic=topic).first()
    return render_template("question.html", question=question)


@app.after_request
def add_header(response):
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=1'
    return response


@app.errorhandler(404) #Pagina de Error: No Existe
def page_not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(401)
def page_not_found(error): #Pagina de Error: Acceso Denegado
    return redirect(url_for("login"))

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
    users = models.User.query.filter_by(tw_username=resp['screen_name'].lower()).all()
    print len(users)
    if len(users) > 0:
        cur_user = users[0]
        login_user(cur_user)
        flash('You were logged in')
        return redirect(url_for("home"))

    return render_template("register.html", username=resp['screen_name'], tw_username=resp['screen_name'])

# FB Stuff!
# *************************************

@app.route('/login/fb')
def fb_login():
    callback = url_for('facebook_authorized', next=request.args.get('next') or request.referrer or None,
                       _external=True)
    return facebook.authorize(callback=callback)


@app.route('/login/fb/authorized')
@facebook.authorized_handler
def facebook_authorized(resp):
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
        user = models.User.query.get(unicode(request.form["username"]))
        if not isinstance(user, type(None)):
            if request.form['password'] == user.password:
                login_user(user)
                # session["user"] = user.username
                return redirect(url_for("home"))
            else:
                error = u"Contraseña Incorrecta"
                return render_template("login.html", error=error)
        else:
            error = u"El usuario seleccionado no existe"
            return render_template('login.html', error=error)
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('user', None)
    return redirect(url_for('home'))


@app.route("/forgot_password")
def forgot_password():
    return render_template("login.html")

@app.route("/profile")
@login_required
def profile():
    return render_template("user.html", user=current_user)

@app.route("/user/<user>")
def user(user):
    user = models.User.query.filter_by(username=user).first()
    if isinstance(user, type(None)):
        return abort(404)
    else:
        user_scores = [] # sorted by topic id
        topics = models.Topic.query.all()
        for topic in topics:
            scores = models.UserScore.query.filter_by(user_username=user.username)
            numbers = [x.score for x in scores if x.question.topic.id==topic.id]
            user_scores.append(sum(numbers))
        max_scores = [] # must be sorted by topic id too
        for topic in topics:
            questions = models.Question.query.filter_by(topic_id=topic.id)
            numbers = [x.max_score for x in questions]
            max_scores.append(sum(numbers))
        return render_template("user.html", user=user, user_scores=user_scores, max_scores=max_scores, topics=topics)

@app.route("/profile/edit", methods=['GET', 'POST'])
@login_required
def edit_user():
    if request.method == 'POST':
        try:
            if request.form["tos"] == "on":
                pass
        except:
            return render_template("edit_user.html", error=u"Aceptar TOS")
        if request.form["password"] == current_user.password:
            #Si Cambio de Email
            if request.form["email"] != current_user.email:
                if isinstance(models.User.query.filter_by(email=request.form["email"]).first(), type(None)):
                    email = request.form["email"]
                else:
                    return render_template("edit_user.html", error=u"Correo ya usado por otro usuario")
            else:
                email = current_user.email
            #Si Cambio la Contraseña
            if is_empty(request.form["new_password"]):
                password = current_user.password
            else:
                password = request.form["new_password"]
            first_name = request.form["first_name"]
            last_name = request.form["last_name"]
            if is_empty(request.form["image"]):
                photo = current_user.photo
            else:
                photo = request.form["image"]
            #Actualizar usuario
            current_user.first_name = first_name
            current_user.last_name = last_name
            current_user.email = email
            current_user.password = password
            current_user.photo = photo
            db.session.commit()
            return redirect(url_for("user", user=current_user.username))
        else:
            logout_user()
            session.pop('user', None)
            return render_template("login.html", error=u"Contraseña Incorrecta En El Formulario")
    return render_template("edit_user.html")
