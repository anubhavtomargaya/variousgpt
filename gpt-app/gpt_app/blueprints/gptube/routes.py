

from pathlib import Path
from http.client import HTTPException

from gpt_app.common.utils_dir import _load_chunks_summary_doc, load_transcript_doc
 

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

### get text at various stage 

@gpt_app.route('/view/transcript/<file_name>')
def get_transcript(file_name):

    text = load_transcript_doc(f'{file_name}')
    return jsonify(text)

@gpt_app.route('/view/summary/<file_name>')
def get_summary(file_name):

    text = _load_chunks_summary_doc(f'{file_name}')
    return jsonify(text)
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

