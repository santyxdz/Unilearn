# -*- coding: utf8 -*-
from flask import Flask, g, url_for, request, flash, json, session,\
    redirect, render_template, abort, send_from_directory
from flask_login import login_user, logout_user, current_user, login_required
from sqlalchemy.exc import IntegrityError
from app import models, app, configs, login_manager
from app import db
from oauth import OAuthSignIn


from flask import make_response
from functools import wraps, update_wrapper
from datetime import datetime

def json_results(question):
    result = {}
    for x in question.answers:
        result.update(json.loads(x.text))
    return json.dumps(result)

def just_admins(f):
    @wraps(f)
    def admin(*args, **kwargs):
        if current_user.type != "admin":
            return redirect(url_for('home'))
        return f(*args,**kwargs)
    return admin

def just_teachers(f):
    @wraps(f)
    def teacher(*args, **kwargs):
        if current_user.type != "teacher" and current_user.type != "admin":
            return redirect(url_for('home'))
        return f(*args,**kwargs)
    return teacher


"""def nocache(view):
    @wraps(view)
    def no_cache(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers['Last-Modified'] = datetime.now()
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        return response

    return update_wrapper(no_cache, view)"""


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
def help_equation(topic):
    helps = models.HelpEquations.query.filter_by(topic_id=topic.id)
    return helps

@app.template_global()
def help_theory(topic):
    helps = models.HelpTheory.query.filter_by(topic_id=topic.id)
    return helps

@app.template_global()
def sort_topic(topic):
    topic.questions.sort(key=lambda x: x.id)
    return ""

@app.template_global()
def total_scores():
    return sum([x.score for x in models.UserScore.query.all()])

@app.template_global()
def progress(user,topic_id):
     scores = models.UserScore.query.filter_by(user_username=user.username).all()
     allquestion = len(models.Question.query.filter_by(topic_id=topic_id).all())
     cont = 0
     for x in scores:
         if x.question.topic_id == topic_id:
             cont +=1
     try:
        return (cont*100)/allquestion
     except ZeroDivisionError as e:
         return 100

@app.template_global()
def is_none(object):
    return isinstance(object,type(None))

@login_manager.user_loader
def load_user(user):
    return models.User.query.get(user)


@app.route("/home")
@app.route("/main")
@app.route('/index')
@app.route('/')
#@nocache
def home():
    return render_template('home.html')


@app.route("/register", methods=['POST', 'GET'])
def register():
    username = request.args.get('username')
    social_id = request.args.get('social_id')
    email = request.args.get('email')
    if request.method == 'POST':
        if request.form["cpassword"]!=request.form["password"]:
            return render_template("register.html", error=u"Las contraseñas no coinciden")
        if request.method == "POST":
            users = models.User.query.filter_by(username=request.form["username"].lower()).all()
            if len(users) > 0:
                return render_template("register.html", error=u"El nombre de usuario ya se encuentra registrado")
            else:
                if "social_id" in request.form:
                    user = models.User(request.form["username"].lower(), request.form["email"],
                                   request.form["password"])
                    user.social_id = request.form["social_id"]
                else:
                    user = models.User(request.form["username"].lower(), request.form["email"],
                                   request.form["password"])
                user.life = 9
                try:
                    db.session.add(user)
                    db.session.commit()
                    login_user(user)
                except IntegrityError:
                    return render_template("register.html",error="El correo seleccionado ya corresponde a otro usuario")
                return redirect(url_for("home"))
    return render_template("register.html",username=username,social_id=social_id,email=email)


@app.route("/users")
#@nocache
def users():
    users_list = models.User.query.all()
    return render_template("users.html", users=users_list)

@app.route("/store")
def store():
    return render_template("store.html")



@app.route("/courses")
#@nocache
def courses():
    public_courses = list(set(models.Topic.query.order_by(models.Topic.id).all()) - \
        set(models.Course.query.all()))
    public_courses.sort(key=lambda x: x.id, reverse=False)
    if current_user.is_authenticated():
        inscribed = models.Topic.query.filter_by(id=current_user.cur_topic_id).first()
        if inscribed is not None:
            return render_template("courses.html", courses=public_courses, active_topic=inscribed.name)
    return render_template("courses.html", courses=public_courses)\

@app.route("/courses/private")
#@nocache
@login_required
def private_courses():
    return render_template("private_courses.html", courses=current_user.courses.all(), \
                           subjects=current_user.subjects.all())

@app.route("/test")
def test():
    return render_template("test.html")

@app.route("/start")
def start():
    return render_template("start_learning.html")

@app.route("/courses/<course>")
#@nocache
def course(course):
    course = models.Topic.query.filter_by(name=course).first()
    if isinstance(course,type(None)):
        return abort(404)
    return render_template("course.html", course=course)

@app.route("/courses/<course>/q/<int:num>")
#@nocache
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

@app.route('/static/<path:path>')
def send_image(path):
    return send_from_directory('static', path)
"""
@app.errorhandler(401)
def not_access(error): #Pagina de Error: Acceso Denegado
    return redirect(url_for("login"))
"""

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        user = models.User.query.get(unicode(request.form["username"].lower()))
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

"""
*******************************************************************************
*********************************** PANEL *************************************
*******************************************************************************
"""

@app.route("/panel")
@login_required
@just_teachers
def panel():
    return render_template("panel.html", models=models)

@app.route("/panel/courses")
@login_required
@just_admins
def courses_panel():
    courses=models.Topic.query.all()
    subjects = models.Course.query.all()
    courses = list(set(courses)-set(subjects))
    return render_template("courses_panel.html", courses=courses,
                           subjects=subjects)

@app.route("/panel/courses/new")
@login_required
@just_admins
def new_course():
    return render_template("new_course.html")

@app.route("/panel/courses/<int:course_id>/edit")
@login_required
@just_admins
def edit_course(course_id=None):
    if isinstance(course_id,type(None)):
        return abort(404)
    topic = models.Topic.query.get(course_id)
    if isinstance(topic,type(None)):
        return abort(404)
    return render_template("edit_course.html", topic=topic)

@app.route("/panel/courses/<int:course_id>")
@login_required
@just_admins
def view_course(course_id=None):
    if isinstance(course_id,type(None)):
        return abort(404)
    topic = models.Topic.query.get(course_id)
    if isinstance(topic,type(None)):
        return abort(404)
    return render_template("view_course.html", topic=topic)

@app.route("/panel/courses/<int:course_id>/question/new")
@login_required
@just_admins
def new_question(course_id=None):
    if isinstance(course_id,type(None)):
        return abort(404)
    topic = models.Topic.query.get(course_id)
    if isinstance(topic,type(None)):
        return abort(404)
    return render_template("new_question.html",topic=topic, models=models)

@app.route("/panel/courses/<int:course_id>/question/<int:question_id>")
@login_required
@just_admins
def view_question(course_id=None,question_id=None):
    if isinstance(course_id,type(None)) or isinstance(question_id,type(None)):
        return abort(404)
    question = models.Question.query.filter_by(topic_id=course_id,id=question_id).first()
    if isinstance(question,type(None)):
        return abort(404)
    return render_template("view_question.html",question=question,models=models)

@app.route("/panel/courses/<int:course_id>/question/<int:question_id>/edit")
@login_required
@just_admins
def edit_question(course_id=None,question_id=None):
    if isinstance(course_id,type(None)) or isinstance(question_id,type(None)):
        return abort(404)
    question = models.Question.query.filter_by(topic_id=course_id,id=question_id).first()
    if isinstance(question,type(None)):
        return abort(404)
    return render_template("edit_question.html",question=question, models=models)
"""
*******************************************************************************
****************************** PANEL - TEACHER ********************************
*******************************************************************************
"""
@app.route("/panel/subjects")
@login_required
@just_teachers
def subjects_panel():
    return render_template("subjects_panel.html", courses=current_user.subjects.all())

@app.route("/panel/subjects/new")
@login_required
@just_teachers
def new_subject():
    return render_template("new_subject.html")

@app.route("/panel/subjects/<int:course_id>/edit")
@login_required
@just_teachers
def edit_subject(course_id=None):
    if isinstance(course_id,type(None)):
        return abort(404)
    topic = current_user.subjects.filter_by(id=course_id).first()
    if isinstance(topic,type(None)):
        return abort(404)
    return render_template("edit_subject.html", topic=topic)

@app.route("/panel/subjects/<int:course_id>")
@login_required
@just_teachers
def view_subject(course_id=None):
    if isinstance(course_id,type(None)):
        return abort(404)
    topic = models.Course.query.get(course_id)
    if isinstance(topic,type(None)):
        return abort(404)
    return render_template("view_subject.html", topic=topic)

@app.route("/panel/subjects/<int:course_id>/question/new")
@login_required
@just_teachers
def new_subject_question(course_id=None):
    if isinstance(course_id,type(None)):
        return abort(404)
    topic = models.Course.query.get(course_id)
    if isinstance(topic,type(None)):
        return abort(404)
    return render_template("new_question.html",topic=topic, models=models)

@app.route("/panel/subjects/<int:course_id>/question/<int:question_id>")
@login_required
@just_teachers
def view_subject_question(course_id=None,question_id=None):
    if isinstance(course_id,type(None)) or isinstance(question_id,type(None)):
        return abort(404)
    question = models.Question.query.filter_by(topic_id=course_id,id=question_id).first()
    if isinstance(question,type(None)):
        return abort(404)
    return render_template("view_question.html",question=question, models=models)

@app.route("/panel/subjects/<int:course_id>/question/<int:question_id>/edit")
@login_required
@just_teachers
def edit_subject_question(course_id=None,question_id=None):
    if isinstance(course_id,type(None)) or isinstance(question_id,type(None)):
        return abort(404)
    question = models.Question.query.filter_by(topic_id=course_id,id=question_id).first()
    if isinstance(question,type(None)):
        return abort(404)
    return render_template("edit_question.html",question=question,models=models)



#Social Network Working in local
@app.route('/authorize/<provider>')
def oauth_authorize(provider):
    try:
        if not current_user.is_anonymous():
            return redirect(url_for('index'))
        oauth = OAuthSignIn.get_provider(provider)
        return oauth.authorize()
    except Exception as e:
        return unicode(e)

@app.route('/callback/<provider>')
def oauth_callback(provider):
    try:
        if not current_user.is_anonymous():
            return redirect(url_for('index'))
        oauth = OAuthSignIn.get_provider(provider)
        social_id, username, email = oauth.callback()
        if social_id is None:
            flash('Authentication failed.')
            return redirect(url_for('index'))
        user = models.User.query.filter_by(social_id=social_id).first()
        if not user:
            return redirect(url_for("register",username=username,social_id=social_id,email=email))
            #return "<p>"+social_id+"<br/>"+username+"<br/>"+set_default(email,"Twitter")+"</p>"
            #user = models.User(social_id=social_id, username=username, email=email)
            #db.session.add(user)
            #db.session.commit()
        login_user(user, True)
        return redirect(url_for('home'))
    except Exception as e:
        return unicode(e)
