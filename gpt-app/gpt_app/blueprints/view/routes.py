from http.client import HTTPException
from flask import jsonify, render_template,redirect,url_for
from flask import current_app as app,jsonify,request

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
    pl = request.args.get('pl', "FileName")
    return render_template('embed.html',placeholder=pl)


@view_app.route('/etc')
def etc():
    mthd = request.method
    args = request.args
    app.logger.info('method: %s',mthd)
    app.logger.info('args: %s',args)
    if mthd =='GET':
        print("get wont work in reality")
        file_name = args.get('title') or None
        
    
    else:raise HTTPException("Invalid Method")
    
    return redirect(url_for('view_app.embed'))



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
