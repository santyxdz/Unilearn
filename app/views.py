# -*- coding: utf8 -*-
from flask import render_template, redirect, session, url_for, request, json
from app import models, app, db

@app.route("/main")
@app.route('/index')
@app.route('/')
def home():
    return render_template('home.html')

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