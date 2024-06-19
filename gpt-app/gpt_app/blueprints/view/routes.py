from flask import render_template
from . import view_app

@view_app.route('/')
def index():
    return render_template('conch.html')

@view_app.route('/chat/')
def chat(file_name):
    
    return render_template('conch.html',title=file_name)

@view_app.route('/submit')
def submit():
    return render_template('submit.html')

@view_app.route('/<path:path>')
def catch_all(path):
    return render_template('conch.html')