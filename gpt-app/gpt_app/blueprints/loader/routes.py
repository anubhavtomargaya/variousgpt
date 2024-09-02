IMPORT_BUCKET = 'uploads-mr-pdf'
from flask import current_app as app,jsonify, render_template,request,redirect,url_for
from http.client import HTTPException
from .load_pdf import load_pdf_into_bucket, load_pdf_link_into_bucket
from .service_process_pdf import process_pdf_to_doc
from  gpt_app.common.session_manager import get_user_email, login_required,is_logged_in
from . import loader_app


@loader_app.route('/')
def index():
    # if is_logged_in():
    return render_template('nsubmit.html')
    # else:
        # return "Please Login to continue"

@loader_app.route('/status')
# #@login_required
def proc_pdf():
    file = request.args.get('file', None)

    if not file:
        raise HTTPException("File not found")
    
    return render_template('nembd.html',title=file)

@loader_app.route('/upload', methods=['POST'])
def upload_file():
    print("starting upload file")

    if 'file' in request.files:
        file = request.files['file']
        print("type of file")
        print(type(file))

        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        file_url = load_pdf_into_bucket(file,destination_filename=file.filename,bucket=IMPORT_BUCKET)
        file_name = str(file_url).split('/')[-1]
        return jsonify({'message': 'File successfully uploaded', 'file_name': file_name}), 200
    
    elif 'pdf_link' in request.form:
        pdf_link = request.form['pdf_link']
        print("type of pdf_link")
        print(type(pdf_link))

        if pdf_link == '':
            return jsonify({'error': 'No PDF link provided'}), 400

        file_url = load_pdf_link_into_bucket(pdf_link,bucket=IMPORT_BUCKET)  # Implement this function to handle the link
        file_name = str(file_url).split('/')[-1]
        return jsonify({'message': 'PDF link successfully uploaded', 'file_name': file_name}), 200
    
    else:
        return jsonify({'error': 'No file or link part'}), 400

    
@loader_app.route('/process/pdf', methods=['POST','GET'])
# @login_required
def process_pdf():

    if not is_logged_in():
        print('not loggede in!')

        # redirect(url_for('google_auth.login'))
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
    print(file ,'file')
    return jsonify(process_pdf_to_doc(file=file,added_by=get_user_email()))
