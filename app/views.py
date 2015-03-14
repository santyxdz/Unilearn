from flask import render_template, redirect, session, url_for, request, json, g
from facebook import get_user_from_cookie, GraphAPI
from app import app
from app import api
from app import models
# ,db
# -*- coding: utf8 -*-
from flask import render_template, redirect, session, url_for, request, json
from app import models, app, db, rest, configs
from flask_oauth import OAuth, OAuthException

oauth = OAuth()
facebook = oauth.remote_app('facebook',
                            base_url='https://graph.facebook.com/',
                            request_token_url=None,
                            access_token='/oauth/access_token',
                            authorize_url='https://www.facebook.com/dialog/oauth',
                            consumer_key=configs.FB_APP_ID,
                            consumer_secret=configs.FB_APP_SECRET,
                            request_token_params={'scope': 'email'})


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


@app.route("/login")
def login():
    callback = url_for(
        'facebook_authorized',
        next=request.args.get('next') or request.referrer or None,
        _external=True
    )
    return facebook.authorize(callback=callback)


@app.route('/login/authorized')
def facebook_authorized():
    resp = facebook.authorized_response()
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    if isinstance(resp, OAuthException):
        return 'Access denied: %s' % resp.message
    session['oauth_token'] = (resp['access_token'], '')
    me = facebook.get('/me')
    return 'Logged in as id=%s name=%s redirect=%s' % \
           (me.data['id'], me.data['name'], request.args.get('next'))


@facebook.tokengetter
def get_facebook_oauth_token():
    return session.get('oauth_token')
