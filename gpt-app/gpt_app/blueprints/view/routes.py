from http.client import HTTPException
from flask import jsonify, render_template,redirect,url_for
from flask import current_app as app,jsonify,request
from gpt_app.common.session_manager import get_user_email
from gpt_app.common.utils_dir import _load_chunks_diarized_doc, _load_chunks_segment_doc, _load_chunks_summary_doc, check_digest_dir, check_question_dir, list_embedding_dir, load_question_doc, load_transcript_doc, save_questions_doc, update_transcript_doc
from gpt_app.common.supabase_handler import get_file_extn_doc, get_list_docs, get_list_transcripts
from gpt_app.blueprints.gptube.service_embed_text import get_analyst_questions
from gpt_app.blueprints.gptube.service_process_pdf import get_pdf_txt, get_transcript_text
from . import view_app

@view_app.route('/')
def index():
    return render_template('chat.html',user=get_user_email())

@view_app.route('chat/<file_name>')
def chat(file_name):
    
    return render_template('chat.html',title=file_name,user=get_user_email())

@view_app.route('/submit')
def submit():
    return render_template('submit.html')

@view_app.route('/file')
def file_upload():
    return render_template('getfile.html')

@view_app.route('/embed')
def embed():
    pl = request.args.get('pl', "FileName")
    return render_template('embed.html',placeholder=pl)

@view_app.route('/procpdf')
def proc_pdf():
    file = request.args.get('file', None)
    if not file:
        raise HTTPException("File not found")
    
    return render_template('nembd.html',title=file)


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
class HistoryQA:
    def __init__(self,
                 timestamp,
                 question,
                 answer,
                 **args) -> None:
        self.timestamp = timestamp
        self.question = question
        self.answer = answer

from gpt_app.common.record_handler import load_qa_record,QARecord,save_qa_record
@view_app.route('/transcript/<file_name>')
def get_transcript(file_name):

    text = load_transcript_doc(f'{file_name}',gcs=True)
    return jsonify(text)


@view_app.route('/document/<file_name>')
def get_document(file_name): #process pdf and show
    print('fil')
    print(file_name)
    # text = load_transcript_doc(f'{file_name}',gcs=True)
    extension = get_file_extn_doc(file_name)['extn']
    print("extension")
    print(extension)
    if extension =='pdf':
        txt = get_pdf_txt(file_name)
    elif extension =='json':

        print("json inside")
        txt = get_transcript_text(file_name)
    else:
        txt =  get_pdf_txt(file_name)
    
    return {'text':txt}

@view_app.route('/records/<file_name>',methods=['POST','GET'])
def get_records(file_name):
    mthd = request.method
   
    app.logger.info('method: %s',mthd)
    if mthd =='POST':
        print("POST")
        args = request.get_json()
        # file_name = args.get('file_name') or None
    # else:raise HTTPException("Invalid Method")
    email =  get_user_email()
    records = load_qa_record()
    user_file_records = [ HistoryQA(**x ).__dict__ for x in records if (x['filename']==file_name and x['email']==email)]
    user_file_records.reverse()
    return jsonify(user_file_records)

@view_app.route('/transcript/update/<file_name>',methods=['POST'])
def update_transcript(file_name):
    mthd = request.method
   
    app.logger.info('method: %s',mthd)
   
    if mthd =='POST':
        print("POST")
        args = request.get_json()
        updated_text = args.get('updated_text') or None
    else:raise HTTPException("Invalid Method")

    up_file = update_transcript_doc(filename=file_name,text=updated_text)


    return jsonify(up_file.stem)
    # return redirect(url_for('view_app.embed'))



@view_app.route('/summary/<file_name>')
def get_summary(file_name):

    text = _load_chunks_summary_doc(f'{file_name}')
    return jsonify(text)

@view_app.route('/dized/<file_name>')
def get_diarized_transcript(file_name):

    text = _load_chunks_diarized_doc(f'{file_name}')
    
    return jsonify(text)

@view_app.route('/segments/<file_name>')
def get_segmented_transcript(file_name):

    text = _load_chunks_segment_doc(f'{file_name}')
    
    return jsonify(text)
 
@view_app.route('/questions/<file_name>') #instead of this add view for view/transcript/ here
def get_analyst_questions_transcript(file_name):
    if check_question_dir(file_name):
        doc = load_question_doc(filename=file_name)
    else:
        doc = get_analyst_questions(file_name)
        if not save_questions_doc(doc,file_name ):
            raise HTTPException("Error saving questions doc..")
    return jsonify(doc)  


@view_app.route('/docs/list')
def list_calls():
    # list = list_embedding_dir()
    list = get_list_docs()
    # list = get_list_transcripts()
    
    # import time
    # time.sleep(.1)
    return jsonify(list)

# @view_app.route('/<path:path>')
# def catch_all(path):
#     return render_template('.html')
