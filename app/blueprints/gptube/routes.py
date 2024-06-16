

from authlib.client import OAuth2Session
from http.client import HTTPException
from .load_youtube_audio import download_youtube_audio
from flask import current_app as app,jsonify,request, url_for, redirect,render_template
import flask 
import ast
import json 

from common.session_manager import set_auth_state,set_auth_token, clear_auth_session, get_next_url,is_logged_in
from common.constants import *


from . import gpt_app, no_cache

@gpt_app.route('/')
def index():
    if is_logged_in():
        return "Already logged in, proceed to /gptube/submit"
    else:
        return "Please Login to continue"

@gpt_app.route('/yt/submit', methods=['POST','GET'])
def submit_youtube():
    mthd = request.method 
    args = request.args
    app.logger.info('method: %s',mthd)
    app.logger.info('args: %s',args)
    if not mthd =='GET':
        print("get wont work in reality")
        # raise HTTPException("Invalid HTTP Method for the endpoing %s",mthd)
    
    ###prcess arguements 

    url = args.get('url') or None

    if not url:
        raise HTTPException("Submit a valid youtube URL")
    ## download url 
    result = download_youtube_audio(url=url) # saves to YOUTUBE_DIR returns a meta
    print(result.__dict__)
    audio_file = Path(result.file_path).name
    result.file_path
    file = Path(result.file_path).name
    return jsonify(result.__dict__)

   
    

@gpt_app.route('/question/{file_name}')
def answer_question():
    return 

