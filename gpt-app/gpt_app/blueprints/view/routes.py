from flask import render_template
from . import view_app

@view_app.route('/')
def index():
    return render_template('index.html')

@view_app.route('/<path:path>')
def catch_all(path):
    return render_template('index.html')