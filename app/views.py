<<<<<<< HEAD
from flask import render_template, redirect, session, url_for, request, json, g
from facebook import get_user_from_cookie, GraphAPI
from app import app
from app import api
from app import models
#,db
=======
# -*- coding: utf8 -*-
from flask import render_template, redirect, session, url_for, request, json
from app import models, app, db, rest
>>>>>>> 3975da2cc914af3774f5646c427369c04b7f642d



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

@app.route('/login')
def login():
    if g.user:
        return render_template('login.html', app_id=configs.FB_APP_ID,
                                app_name=configs.FB_APP_NAME, user=g.user)

@app.route('/logout')
def logout():
    session.pop('user',None)
    return redirect(url_for('index'))

@app.before_request
def get_current_user():
    if session.get('user'):
        g.user = session.get('user')
        return

    result = get_user_from_cookie(cookies=request.cookies,
                                    app_id=configs.FB_APP_ID,
                                    app_secret=configs.FB_APP_SECRET)

    if result:
        user = User.query.filter(User.id == result['uid']).first()

        if not user:
            graph = GraphAPI(result['access_token'])
            profile = graph.get_object('me')
            user = User(id=str(profile['id']), name=profile['name'],
                        profile_url=profile['link'],
                        access_token=result['access_token'])
        elif user.access.token != result['access_token']:
            user.access.token = result['access_token']

        session['user'] = dict(name=user.name, profile_url=user.profile_url,
                            id = user.id, access_token=user.access_token)
    g.user = session.get('user', None)
    return render_template('login.html',name=profile['name'],
                           profile=profile['link'],access_token=result['access_token'],
                           id=profile['id'])
