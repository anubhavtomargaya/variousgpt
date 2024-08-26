from http.client import HTTPException
import re
from flask import jsonify, make_response, render_template,redirect,url_for
from flask import current_app as app,jsonify,request
from gpt_app.common.session_manager import get_user_email, login_required
from gpt_app.common.utils_dir import _load_chunks_diarized_doc, _load_chunks_segment_doc, _load_chunks_summary_doc, check_digest_dir, check_question_dir, list_embedding_dir, load_question_doc, load_transcript_doc, save_questions_doc, update_transcript_doc
from gpt_app.common.supabase_handler import get_content_top_questions, get_file_extn_doc, get_file_meta, get_itdoc_mg_guidance, get_itdoc_qa_secrion, get_list_docs, get_list_pdf_transcripts, get_list_transcripts, get_pdf_chunks_transcript, get_qa_records
from gpt_app.common.supabase_handler import get_company_transcript_data, get_file_extn_doc, get_list_docs, get_list_pdf_transcripts, get_list_transcripts, get_pdf_chunks_transcript, get_qa_records
from gpt_app.blueprints.gptube.service_embed_text import get_analyst_questions
from gpt_app.blueprints.gptube.service_process_pdf import get_pdf_txt, get_transcript_text
from . import company_app
## prefix -> /company

@company_app.route('/')
# #@login_required
def index():
    return redirect(url_for('company_app.chat_app'))

# @company_app.route('/<company_name>/latest')
# def faq_page(company_name):
#     faq_data = {
#         "What is your return policy?": "We offer a 30-day money-back guarantee on all our products.",
#         "How long does shipping take?": "Shipping typically takes 3-5 business days within the continental US.",
#         # Add more questions and answers as needed
#     }
#     return render_template('company.html', company_name=company_name, faq_data=faq_data)


def slugify(question):
    return re.sub(r'[^\w\s-]', '', question.lower()).strip().replace(' ', '-')

@company_app.app_template_filter('slugify')
def slugify_filter(s):
    return slugify(s)

@company_app.route('/<company_name>/latest')
@company_app.route('/<company_name>/latest/<question_slug>')
def company_latest(company_name, question_slug=None):
    faq_data = {
        "When is the Reliance Concall 2024?": "The Reliance Industries Concall for 2024 is scheduled for May 15, 2024, at 10:00 AM IST.",
        "How can I join the Reliance Concall 2024?": "You can join the Reliance Concall 2024 by visiting the official Reliance website and following the instructions provided under the 'Concall' section."
    }
    
    if question_slug:
        # Check if the slug is valid
        valid_slugs = [slugify(q) for q in faq_data.keys()]
        if question_slug not in valid_slugs:
            # Redirect to the main page if the slug is invalid
            return redirect(url_for('company_latest', company_name=company_name))
    
    return render_template('company.html', company_name=company_name, faq_data=faq_data, question_slug=question_slug)

@company_app.route('/chat')
# #@login_required
def chat_app():
    user = get_user_email()
    if not user:
        history = f"""
        <br/>
        <h3>To Save & Export History </h3>
        <form action="{url_for('google_auth.login')}" method="post">
            <button type="submit" style="display: flex; align-items: center; padding: 10px; border: none; background-color: #ceea99; color: black; font-size: 16px; cursor: pointer; margin: 0px">
                <img src="{url_for('static', filename='images/google-logo.png')}" alt="Google Logo" style="width: 20px; height: 20px; margin-right: 10px;">
                Sign In with Google
            </button>
            <sub style="color: #ddd; font-size:10px;  cursor: pointer; margin: 0px" >Request access first. Write to imanubhav18@gmail.com</sub>
        </form>
        """
        name = ''
    else:
        name = user
        history=f"History"
    return render_template('chat.html',history=history,user=get_user_email())

@company_app.route('/chat/<file_name>')
#@login_required
def chat(file_name):
    user = get_user_email()
    if not user:
        history = f"""
        <br/>
        <h3>To Save & Export History </h3>
        <form action="{url_for('google_auth.login')}" method="post">
            <button type="submit" style="display: flex; align-items: center; padding: 10px; border: none; background-color: #ceea99; color: black; font-size: 16px; cursor: pointer; margin: 0px">
                <img src="{url_for('static', filename='images/google-logo.png')}" alt="Google Logo" style="width: 20px; height: 20px; margin-right: 10px;">
                Sign In with Google
            </button>
            
            
            <p style="color: #ddd; font-size:10px; line-height:1; cursor: pointer; margin: 2px 0px 0px 0px" >Request access first. Write to imanubhav18@gmail.com</p>
        </form>
        """
        name = ''
    else:
        name = user
        history=f"History"
    return render_template('chat.html',title=file_name,history=history,user=name)

@company_app.route('/submit')
#@login_required
def submit():
    return render_template('submit.html')

@company_app.route('/file')
def file_upload():
    return render_template('getfile.html')

@company_app.route('/new')
#@login_required
def new():
    return render_template('nsubmit.html')

@company_app.route('/embed')
def embed():
    pl = request.args.get('pl', "FileName")
    return render_template('embed.html',placeholder=pl)

@company_app.route('/procpdf')
# #@login_required
def proc_pdf():
    file = request.args.get('file', None)
    row = request.args.get('row', None)
    extn = request.args.get('extn', None)

    if not file:
        raise HTTPException("File not found")
    
    return render_template('nembd.html',title=file)


@company_app.route('/etc')
def etc():
    mthd = request.method
    args = request.args
    app.logger.info('method: %s',mthd)
    app.logger.info('args: %s',args)
    if mthd =='GET':
        print("get wont work in reality")
        file_name = args.get('title') or None
        
    
    else:raise HTTPException("Invalid Method")
    
    return redirect(url_for('company_app.embed'))



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
# @company_app.route('/transcript/<file_name>')
# #@login_required
# def get_transcript(file_name):

#     text = load_transcript_doc(f'{file_name}',gcs=True)
#     return jsonify(text)


@company_app.route('/document/<file_name>')
#@login_required
def get_pdf_transcript(file_name): #process pdf and show
    print('fil---')
    print(file_name)
    # text = load_transcript_doc(f'{file_name}',gcs=True)
    # extension = get_f

    details =  get_pdf_chunks_transcript(file_name)
    response= make_response(jsonify({
        'company_name': details['company_name'],
        'quarter': details['quarter'],
        'financial_year': details['financial_year'],
        'text': details['extracted_transcript']
        }))
    response.headers['Cache-Control'] = 'public, max-age=360'  # Cache for 1 hour
    
    return response

    

@company_app.route('/document/section/qa/<file_name>')
#@login_required
def get_qa_section(file_name): #process pdf and show
    print('qa: fil---')
    print(file_name)
    # text = load_transcript_doc(f'{file_name}',gcs=True)
    # extension = get_f

    txt =  get_itdoc_qa_secrion(file_name)
    
    response = make_response ({'file_name':file_name,
            'qa':txt})
    response.headers['Cache-Control'] = 'public, max-age=360'  # Cache for 5min
    
    return response



@company_app.route('/document/section/management/<file_name>')
#@login_required
def get_mg_guidance(file_name): #process pdf and show
    print('qa: fil---')
    print(file_name)
    # text = load_transcript_doc(f'{file_name}',gcs=True)
    # extension = get_f

    txt =  get_itdoc_mg_guidance(file_name)
    
    response = make_response( {'file_name':file_name,
            'management_guidance':txt})
    response.headers['Cache-Control'] = 'public, max-age=360'  # Cache for 5min
    
    return response


@company_app.route('/content/top_questions/<file_name>')
#@login_required
def get_top_questions(file_name): #process pdf and show
    print('top qa: fil---')
    print(file_name)
    # text = load_transcript_doc(f'{file_name}',gcs=True)
    # extension = get_f

    top_questions =  get_content_top_questions(file_name)
    details = get_file_meta(file_name)
    response = make_response(jsonify({
                    'file_name':file_name,
                    'company_name': details['company_name'],
                    'quarter': details['quarter'],
                    'financial_year': details['financial_year'],
                    'top_questions':top_questions
                    
                    }))
    response.headers['Cache-Control'] = 'public, max-age=360'  # Cache for 1 hour
    
    return response




@company_app.route('/records/<file_name>',methods=['POST','GET'])
#@login_required
def get_records(file_name):
    mthd = request.method
   
    app.logger.info('method: %s',mthd)
    if mthd =='POST':
        print("POST")
        args = request.get_json()
        # file_name = args.get('file_name') or None
    # else:raise HTTPException("Invalid Method")
    email =  get_user_email()
    # records = load_qa_record()
    records = get_qa_records(email=email,filename=file_name)
    print('records')
    print(records)
    user_file_records = [ HistoryQA(**x ).__dict__ for x in records if (x['filename']==file_name and x['email']==email)]
    user_file_records.reverse()
    response = make_response(jsonify(user_file_records))
    response.headers['Cache-Control'] = 'public, max-age=360'  # Cache for 1 hour
    return response
    

# @company_app.route('/transcript/update/<file_name>',methods=['POST'])
# #@login_required
# def update_transcript(file_name):
#     mthd = request.method
   
#     app.logger.info('method: %s',mthd)
   
#     if mthd =='POST':
#         print("POST")
#         args = request.get_json()
#         updated_text = args.get('updated_text') or None
#     else:raise HTTPException("Invalid Method")

#     up_file = update_transcript_doc(filename=file_name,text=updated_text)


#     return jsonify(up_file.stem)
#     # return redirect(url_for('company_app.embed'))



# @company_app.route('/summary/<file_name>')
# def get_summary(file_name):

#     text = _load_chunks_summary_doc(f'{file_name}')
#     return jsonify(text)

 
# @company_app.route('/questions/<file_name>') #instead of this add view for view/transcript/ here
# #@login_required
# def get_analyst_questions_transcript(file_name):
#     if check_question_dir(file_name):
#         doc = load_question_doc(filename=file_name)
#     else:
#         doc = get_analyst_questions(file_name)
#         if not save_questions_doc(doc,file_name ):
#             raise HTTPException("Error saving questions doc..")
#     return jsonify(doc)  


@company_app.route('/docs/list')
#@login_required
def list_calls():
    list = get_company_transcript_data()
    
    response = make_response(jsonify(list))
    response.headers['Cache-Control'] = 'public, max-age=3600'  # Cache for 1 hour
    
    return response

# @company_app.route('/<path:path>')
# def catch_all(path):
#     return render_template('.html')
