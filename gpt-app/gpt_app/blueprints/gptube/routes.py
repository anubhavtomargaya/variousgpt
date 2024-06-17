

from pathlib import Path
from authlib.client import OAuth2Session
from http.client import HTTPException
 

from .service_transcribe_audio import create_text_from_audio
from .service_embed_text import create_text_meta_doc,create_embeddings_from_chunk_doc
from .load_youtube_audio import download_youtube_audio
from flask import current_app as app,jsonify,request, url_for, redirect,render_template
import flask 
import ast
import json 

from  gpt_app.common.session_manager import set_auth_state,set_auth_token, clear_auth_session, get_next_url,is_logged_in


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

   
    
@gpt_app.route('/transcribe/youtube', methods=['POST','GET'])
def transcribe_youtube():
    mthd = request.method 
    args = request.args
    app.logger.info('method: %s',mthd)
    app.logger.info('args: %s',args)
    if not mthd =='GET':
        print("get wont work in reality")
        # raise HTTPException("Invalid HTTP Method for the endpoing %s",mthd)
    
    ###prcess arguements 

    title = args.get('title') or None

    
    return jsonify(create_text_from_audio(youtube=True,
                                            file_name=title,
                                            base_prompt=title))
    
    # return the text from json if create is true
    
@gpt_app.route('/embed/', methods=['POST','GET'])
def create_embedding():
    summary_prmpt = "You are a helpful assistant to summarise a quarterly EARNINGS CONFERENCE CALL. The transcript of the call will be provided in chunks as context and you have to extract information carefully and concisely in summaries.  "
    sections_interview =  ['INTRO', 'MANAGEMENT NOTE', 'ANALYST QA', 'CONCLUSION']

    mthd = request.method 
    args = request.args
    app.logger.info('method: %s',mthd)
    app.logger.info('args: %s',args)
    if not mthd =='GET':
        print("get wont work in reality")
        # raise HTTPException("Invalid HTTP Method for the endpoing %s",mthd)
    
    ###prcess arguements 

    title = args.get('title') or None
    chunk_size = args.get('chunk') or 2000

    summariser = create_text_meta_doc(ts_filename=title,
                                      chunk_size=chunk_size,
                                      summariser_prompt=summary_prmpt,
                                      sections=sections_interview)
    if summariser:
        embedding = create_embeddings_from_chunk_doc(filename=title)
    return jsonify(embedding.stem.__str__())


@gpt_app.route('/question/{file_name}')
def answer_question():
    return 

