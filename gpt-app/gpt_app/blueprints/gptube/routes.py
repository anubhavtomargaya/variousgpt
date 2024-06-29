

from pathlib import Path
from http.client import HTTPException

from gpt_app.common.utils_dir import _load_chunks_segment_doc, _load_chunks_summary_doc, _load_digest_doc, check_digest_dir, check_diz_dir, check_segment_dir, check_summary_dir, load_transcript_doc, save_digest_doc
 

from .service_answer_with_corpus import answer_question, get_context_corpus
from .service_transcribe_audio import create_text_from_audio
from .service_embed_text import create_text_diarized_doc, create_text_meta_doc,create_embeddings_from_chunk_doc, create_text_segment_doc, get_qa_digest
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
                                            base_prompt=base_prompt,
                                            ogg=True))
    
    # return the text from json if create is true
    


    
@gpt_app.route('/diarize/', methods=['POST','GET'])
def create_diarization(): 
    dizzer_prompt = "You are a helpful assistant to diarize a quarterly EARNINGS CONFERENCE CALL from text. \
                     The transcript of the call will be provided in chunks as context and you have to format \
                    the text appropriately such that each speaker is mentioned by their name on their turn with\
                    their conversation. Diarization of the previous chunk will be provided for context. \
                    if no previous diarization then assume its the start, otherwise its a continuted convo so be intelligent. \
                    for example : 'speaker_name' :'text said by them' . Return the information as a markdown formatted diarized transcript. "

    default_chunk_embedding  = 2000
    mthd = request.method 
    args = request.args
    app.logger.info('method: %s',mthd)
    app.logger.info('args: %s',args)
    if mthd =='GET':
        title = args.get('title') or None
        chunk_size = args.get('chunk') or default_chunk_embedding  
        user_input = dizzer_prompt
        
    elif mthd=='POST':
        data = request.get_json()

        title = data.get('title') or None
        chunk_size = data.get('chunk') or default_chunk_embedding  
        user_input= data.get('user_prompt') or dizzer_prompt
        
    ###prcess arguements 

    if not title: raise HTTPException("File name of transcript not provided")
    if check_diz_dir(title):
        return jsonify(title)
    dts_file = create_text_diarized_doc(ts_filename=title,
                                      chunk_size=int(chunk_size),
                                      dizer_prompt=user_input )
    

    return jsonify(dts_file.name)
SEGGER_PROMPT = "You are a helpful assistant to segment a quarterly EARNINGS CONFERENCE CALL from text. \
                    The transcript of the con-call will be provided in chunks.\
                    The concall may start with an intro and then some presentation from the management \
                    which can include multiple members as multiple CXOs may talk. At the end there \
                    is a QnA where different fund houses representatives ask questions. And then it ends. \
                    SEGMENT THE TEXT INTO EITHER : PRESENTATION or  QA  \
                    The analyst qa section may have long intervals of a person from management answering the question of the analyst. \
                    when that happens do not call it as Presentation as that is part of the whole QA section. If the section is QA then extract the \
                    questions RELATED TO COMPANY in that text in a list properly and return. Do not extract common conversational questions like 'am I audible?' etc \
                    Otherwise return an empty list in case of presentation : [ ]  \
                    I will provide you with the previous chunk and it's identified SEGMENT as context to make it easy \
                    Response only in json format : { segment: 'PRESNTATION | QA', 'questions':[ {'question':'extracted_concall_question' } , { }, ] }  Note that once the QA section starts \
                    all the other text chunks after that are most probably QA"
    
@gpt_app.route('/segment/', methods=['POST','GET'])
def create_segments():
    
    
    default_chunk_embedding  = 5000
    mthd = request.method 
    args = request.args
    app.logger.info('method: %s',mthd)
    app.logger.info('args: %s',args)
    if mthd =='GET':
        title = args.get('title') or None
        chunk_size = args.get('chunk') or default_chunk_embedding  
        user_input = SEGGER_PROMPT
        
    elif mthd=='POST':
        data = request.get_json()

        title = data.get('title') or None
        chunk_size = data.get('chunk') or default_chunk_embedding  
        user_input= data.get('user_prompt') or SEGGER_PROMPT
        
    ###prcess arguements 

    if not title: raise HTTPException("File name of transcript not provided")
    if check_segment_dir(title):
        doc = _load_chunks_segment_doc(file_name=title)
        return jsonify(doc)
    sts_file = create_text_segment_doc(ts_filename=title,
                                      chunk_size=int(chunk_size),
                                      segger_prompt=user_input )
    

    return jsonify(sts_file.name)
    
@gpt_app.route('/digest/', methods=['POST','GET'])
def create_qa_digest():

    default_chunk_embedding  = 5000
    mthd = request.method 
    args = request.args
    app.logger.info('method: %s',mthd)
    app.logger.info('args: %s',args)
    if mthd =='GET':
        title = args.get('title') or None
       

        
    elif mthd=='POST':
        data = request.get_json()

        title = data.get('title') or None
        
    ###prcess arguements 
    if not title: raise HTTPException("File name of transcript not provided")
    if check_digest_dir(title):
        doc = _load_digest_doc(file_name=title)
        return jsonify(doc['qa_summary']['qa_summary'])
    
    if not check_segment_dir(title):
         if not create_text_segment_doc(ts_filename=title,
                                      chunk_size=int(default_chunk_embedding),
                                      segger_prompt=SEGGER_PROMPT ):
             raise HTTPException("Error getting segment doc!!")
        
        # raise HTTPException("Segmented doc not found to get QA Section. Run /segment/?{ }")
    qa_digest_doc = get_qa_digest(ts_filename=title, )
    filn = save_digest_doc(qa_digest_doc,title)
    print(filn)

    return jsonify(qa_digest_doc['qa_summary']['qa_summary'])


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

