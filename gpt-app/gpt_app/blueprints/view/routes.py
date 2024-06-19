from flask import jsonify, render_template

from gpt_app.common.utils_dir import _load_chunks_summary_doc, load_transcript_doc
from . import view_app

@view_app.route('/')
def index():
    return render_template('conch.html')

@view_app.route('/chat/<file_name>')
def chat(file_name):
    
    return render_template('conch.html',title=file_name)

@view_app.route('/submit')
def submit():
    return render_template('submit.html')


@view_app.route('/embed')
def embed():
    return render_template('embed.html')


### get text at various stage 

@view_app.route('/transcript/<file_name>')
def get_transcript(file_name):

    text = load_transcript_doc(f'{file_name}')
    return jsonify(text)

@view_app.route('/summary/<file_name>')
def get_summary(file_name):

    text = _load_chunks_summary_doc(f'{file_name}')
    return jsonify(text)

@view_app.route('/<path:path>')
def catch_all(path):
    return render_template('conch.html')
