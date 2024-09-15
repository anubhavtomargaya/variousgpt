from flask import jsonify, make_response, render_template,redirect,url_for
from flask import current_app as app,jsonify,request
from gpt_app.common.session_manager import get_user_email, login_required
from gpt_app.common.supabase_handler import get_content_top_questions,  get_file_meta, get_itdoc_mg_guidance, get_itdoc_qa_secrion, get_pdf_chunks_transcript, get_qa_records
from gpt_app.common.supabase_handler import get_company_transcript_data, get_pdf_chunks_transcript, get_qa_records
from . import view_app

@view_app.route('/')
# #@login_required
def index():
    return redirect(url_for('view_app.chat_app'))

@view_app.route('/chat')
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

@view_app.route('/chat/<file_name>')
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

# @view_app.route('/submit')
# #@login_required
# def submit():
#     return render_template('submit.html')

# @view_app.route('/file')
# def file_upload():
#     return render_template('getfile.html')

# @view_app.route('/new')
# #@login_required
# def new():
#     return render_template('nsubmit.html')

# # @view_app.route('/embed')
# # def embed():
# #     pl = request.args.get('pl', "FileName")
# #     return render_template('embed.html',placeholder=pl)

# # @view_app.route('/procpdf')
# # # #@login_required
# # def proc_pdf():
# #     file = request.args.get('file', None)
# #     row = request.args.get('row', None)
# #     extn = request.args.get('extn', None)

# #     if not file:
# #         raise HTTPException("File not found")
    
# #     return render_template('nembd.html',title=file)


# @view_app.route('/etc')
# def etc():
#     mthd = request.method
#     args = request.args
#     app.logger.info('method: %s',mthd)
#     app.logger.info('args: %s',args)
#     if mthd =='GET':
#         print("get wont work in reality")
#         file_name = args.get('title') or None
        
    
#     else:raise HTTPException("Invalid Method")
    
#     return redirect(url_for('view_app.embed'))



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

# from gpt_app.common.record_handler import load_qa_record,QARecord,save_qa_record
# @view_app.route('/transcript/<file_name>')
# #@login_required
# def get_transcript(file_name):

#     text = load_transcript_doc(f'{file_name}',gcs=True)
#     return jsonify(text)


@view_app.route('/document/<file_name>')
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

    

@view_app.route('/document/section/qa/<file_name>')
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



@view_app.route('/document/section/management/<file_name>')
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


@view_app.route('/content/top_questions/<file_name>')
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




@view_app.route('/records/<file_name>',methods=['POST','GET'])
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
def process_transcript(raw_transcript):
    processed_transcript = []
    current_speaker = None
    current_text = []

    print("Raw transcript:", raw_transcript)  # Debug print

    # Ensure raw_transcript is a list
    if isinstance(raw_transcript, dict):
        raw_transcript = list(raw_transcript.values())
    elif not isinstance(raw_transcript, list):
        raise ValueError("Expected raw_transcript to be a list or dict, got {}".format(type(raw_transcript)))

    for item in raw_transcript:
        print("Processing item:", item)  # Debug print
        
        # Ensure item is a dictionary
        if not isinstance(item, dict):
            print("Skipping non-dict item:", item)
            continue

        speaker = item.get('speaker')
        text = item.get('text', '').strip()
        if speaker=='Speaker Name' or speaker=='Speaker':
            speaker='.'
        if not text:
            print("Skipping item with empty text")
            continue

        if speaker != current_speaker:
            if current_speaker is not None:
                processed_transcript.append({'speaker': current_speaker, 'text': ' '.join(current_text)})
            current_speaker = speaker
            current_text = [text]
        else:
            current_text.append(text)

    # Add the last speaker's text
    if current_speaker is not None:
        processed_transcript.append({'speaker': current_speaker, 'text': ' '.join(current_text)})

    print("Processed transcript:", processed_transcript)  # Debug print
    return processed_transcript
@view_app.route('/concall/<file_name>')
def concall(file_name):
    section = request.args.get('section', 'top_questions')
    
    # Fetch company details
    details = get_file_meta(file_name)
    
    # Fetch content based on the selected section
    if section == 'top_questions':
        content = get_content_top_questions(file_name)
        content = {k:str(v).replace("**",'') for k,v in content.items()}
        print("content",content)
        print("type",type(content))
    elif section == 'transcript':
        raw_transcript = get_pdf_chunks_transcript(file_name)['extracted_transcript']
        content = process_transcript(raw_transcript)
        print(content) 
    elif section == 'qa_section':
        content = get_itdoc_qa_secrion(file_name)
        print("con",content)
    elif section == 'management_guidance':
        content = get_itdoc_mg_guidance(file_name)
    
    return render_template('concall.html',
                           company_name=details['company_name'],
                           quarter=details['quarter'],
                           financial_year=details['financial_year'],
                           file_name=file_name,
                           active_section=section,
                           top_questions=content if section == 'top_questions' else {},
                           transcript=content if content and section == 'transcript' else '',
                           qa_section=content if content and section == 'qa_section' else '',
                           management_guidance=content if content and section == 'management_guidance' else '')

# @view_app.route('/transcript/update/<file_name>',methods=['POST'])
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
#     # return redirect(url_for('view_app.embed'))



# @view_app.route('/summary/<file_name>')
# def get_summary(file_name):

#     text = _load_chunks_summary_doc(f'{file_name}')
#     return jsonify(text)

 
# @view_app.route('/questions/<file_name>') #instead of this add view for view/transcript/ here
# #@login_required
# def get_analyst_questions_transcript(file_name):
#     if check_question_dir(file_name):
#         doc = load_question_doc(filename=file_name)
#     else:
#         doc = get_analyst_questions(file_name)
#         if not save_questions_doc(doc,file_name ):
#             raise HTTPException("Error saving questions doc..")
#     return jsonify(doc)  


@view_app.route('/docs/list')
#@login_required
def list_calls():
    list = get_company_transcript_data()
    
    response = make_response(jsonify(list))
    response.headers['Cache-Control'] = 'public, max-age=3600'  # Cache for 1 hour
    
    return response

# @view_app.route('/<path:path>')
# def catch_all(path):
#     return render_template('.html')
