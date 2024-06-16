

from authlib.client import OAuth2Session
from flask import current_app, url_for, redirect
import flask 
import ast
import json 

from common.session_manager import set_auth_state,set_auth_token, clear_auth_session, get_next_url,is_logged_in
from common.constants import *
from .gpt_service import get_user_info


from . import gpt_app, no_cache

@gpt_app.route('/')
def index():
    if is_logged_in():
        return "Already logged in, proceed to /gptube/submit"
    else:
        return "Please Login to continue"

@gpt_app.route('/yt/submit')
def submit_youtube():pass
   
    

@gpt_app.route('/question/{file_name}')
def answer_question():
    return 

