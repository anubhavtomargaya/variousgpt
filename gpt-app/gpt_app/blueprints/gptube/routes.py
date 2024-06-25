

from pathlib import Path
from http.client import HTTPException

from gpt_app.common.utils_dir import _load_chunks_summary_doc, check_summary_dir, load_transcript_doc
 

from .service_answer_with_corpus import answer_question, get_context_corpus
from .service_transcribe_audio import create_text_from_audio
from .service_embed_text import create_text_meta_doc,create_embeddings_from_chunk_doc
from .load_youtube_audio import download_youtube_audio
from flask import current_app as app,jsonify,request, url_for, redirect,render_template


from  gpt_app.common.session_manager import set_auth_state,set_auth_token, clear_auth_session, get_next_url,is_logged_in


from . import gpt_app

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
    if mthd =='GET':
        print("get wont work in reality")
        url = args.get('url') or None
        # raise HTTPException("Invalid HTTP Method for the endpoing %s",mthd)
    elif mthd=='POST':
     
        data = request.get_json() 
        url = data.get('url') or None

    else:raise Exception("Invalid Method")
    ###prcess arguements 

   

    if not url:
        raise HTTPException("Submit a valid youtube URL")
    ## download url 
    result = download_youtube_audio(url=url) # saves to YOUTUBE_DIR returns a meta
    print(result)
    print(result.__dict__ )
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
    if mthd =='GET':
        print("get wont work in reality")
        title = args.get('title') or None
        
    elif mthd=='POST':
        data = request.get_json()

        title  = data.get('title') or None
        user_input= data.get('user_prompt') or ''
        base_prompt = f"{title}"  + user_input

    else:raise HTTPException("Invalid Method")
    
    ###prcess arguements 
    if not title:
        raise HTTPException("title not provided ")
        
    return jsonify(create_text_from_audio(youtube=True,
                                            file_name=title,
                                            base_prompt=base_prompt))
    
    # return the text from json if create is true
    
@gpt_app.route('/embed/', methods=['POST','GET'])
def create_embedding():
    summary_prmpt = "You are a helpful assistant to summarise a quarterly EARNINGS CONFERENCE CALL. The transcript of the call will be provided in chunks as context and you have to extract information carefully in summaries.  "
    sections_default =  ['INTRO', 'MANAGEMENT NOTE', 'ANALYST QA', 'CONCLUSION']
    default_chunk_embedding  = 2000
    mthd = request.method 
    args = request.args
    app.logger.info('method: %s',mthd)
    app.logger.info('args: %s',args)
    if mthd =='GET':
        title = args.get('title') or None
        chunk_size = args.get('chunk') or default_chunk_embedding  
        
    elif mthd=='POST':
        data = request.get_json()

        title = data.get('title') or None
        chunk_size = data.get('chunk') or default_chunk_embedding  
        user_input= data.get('user_prompt') or summary_prmpt
        
    ###prcess arguements 

    if not title: raise HTTPException("File name of transcript not provided")
    if check_summary_dir(title):
        return jsonify(title)
    summariser = create_text_meta_doc(ts_filename=title,
                                      chunk_size=int(chunk_size),
                                      summariser_prompt=user_input,
                                      sections=sections_default)
    if summariser:
        embedding = create_embeddings_from_chunk_doc(filename=title)

    return jsonify(embedding.stem.__str__())


from flask import current_app as app
from .service_answer_with_corpus import question_prompt
@gpt_app.route('/question/<file_name>', methods=['GET','POST'])
def answer_question_(file_name):
    
    mthd = request.method 
    args = request.args

    app.logger.info('method: %s',mthd)
    app.logger.info('args: %s',args)
    if mthd =='GET':
        print("get wont work in reality")
        question = args.get('question') or None

    if mthd=='POST':
        data = request.get_json() 
        question = data.get('question')


    ###prcess arguements 

    # title = args.get('title') or None
    print(file_name)
    app.logger.info('body: %s',data)

    if not (file_name or question):
        raise HTTPException("Please input args")
    
    try:
        doc = get_context_corpus(file_name=file_name,)
    except Exception as e:
        raise HTTPException(f"{file_name}: file not present, Error : {e}")
    
    a = answer_question(file_name=file_name,
                    doc=doc,
                    question=question,
                    question_prompt=question_prompt,
                    _top_n=3
                    )
    return jsonify(a)

