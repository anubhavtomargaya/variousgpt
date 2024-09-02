

from http.client import HTTPException
from flask import current_app as app,jsonify,request

from  gpt_app.common.session_manager import get_user_email, login_required,is_logged_in

from .service_process_tdoc import process_transcripton_doc_to_rag
from .service_answer_with_corpus import answer_question, question_prompt, get_context_corpus_database
from .service_transcribe_audio import create_text_from_audio
from .load_youtube_audio import download_youtube_audio

APP_BUCKET = 'gpt-app-data'
PROC_PDF_BUCKET = 'pdf-transcripts'
from . import gpt_app

@gpt_app.route('/')
def index():
    if is_logged_in():
        return "Already logged in, proceed to /gptube/submit"
    else:
        return "Please Login to continue"

@gpt_app.route('/yt/submit', methods=['POST','GET'])
@login_required
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
    # check if alreayd downloaded: fetch meta if exists and return 
    result = download_youtube_audio(url=url) # saves to YOUTUBE_DIR returns a meta
    print(result)
    if not result:
        raise HTTPException("Unable to download the audio")
    # print(result.__dict__ )
    if not isinstance(result,dict):
        r = result.__dict__
    else:
        r = result
    # audio_file = Path(result.file_path).name
    # result.file_path
    # file = Path(result.file_path).name
    print("rerrrrr")
    print(r)
    return jsonify(r['meta'])

@gpt_app.route('/process/tdoc', methods=['POST','GET'])
@login_required
def process_transcription_doc():
    GCS = True 
    mthd = request.method 
    args = request.args
    app.logger.info('method: %s',mthd)
    app.logger.info('args: %s',args)
    if mthd =='GET':
        print("get wont work in reality")
        file = args.get('file') or None
        
    elif mthd=='POST':
        data = request.get_json()
        file = data.get('file') or None

    else:raise HTTPException("Invalid Method")

    if not file:
        raise HTTPException("title not provided ")
        
    return jsonify(process_transcripton_doc_to_rag(file,added_by=get_user_email()))

@gpt_app.route('/transcribe/youtube', methods=['POST','GET'])
@login_required
def transcribe_youtube():
    GCS = True 
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
        
    return jsonify(create_text_from_audio(
                                            file_name=title,
                                            base_prompt=base_prompt))
    
    # return the text from json if create is true
    

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
        # doc = get_context_corpus(file_name=file_name,)
        doc = get_context_corpus_database(file_name)
        print("got corpus")
        # print(doc)
        # return jsonify(doc)
    except Exception as e:
        raise HTTPException(f"{file_name}: file not present, Error : {e}")
    
    a = answer_question(file_name=file_name,
                    doc=doc,
                    question=question,
                    question_prompt=question_prompt,
                    _top_n=3)
    
    return jsonify(a)

