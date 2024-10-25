IMPORT_BUCKET = 'uploads-mr-pdf'
import time
from flask import current_app as app,jsonify, render_template,request,redirect,url_for
from http.client import HTTPException
from .load_pdf import load_pdf_into_bucket, load_pdf_link_into_bucket
from .service_process_pdf import process_pdf_to_doc
from .worker_logging import generate_process_id, log_pipeline_event,PipelineStage,ProcessStatus
from  gpt_app.common.session_manager import get_user_email, login_required,is_logged_in,set_process_id, get_process_id
from  gpt_app.common.supabase_handler import get_pipeline_events
from . import loader_app


@loader_app.route('/')
def index():
    # if is_logged_in():
    return render_template('nsubmit.html')
    # else:
        # return "Please Login to continue"
@loader_app.route('/status/<process_id>', methods=['GET'])
def get_pipeline_status(process_id):
    try:
        events = get_pipeline_events(process_id)
        
        if not events:
            return jsonify({'error': 'No events found for this process'}), 404
            
        # Get file_name from the first event
        file_name = events[0]['file_name']
            
        # All possible stages in order
        all_stages = ['upload', 'text_extraction', 'qa_generation', 'embedding_generation', 'indexing']
        
        # Get completed and failed stages
        completed_stages = {
            event['stage'] for event in events 
            if event['status'] == 'completed'
        }
        failed_stages = {
            event['stage'] for event in events 
            if event['status'] == 'failed'
        }
        
        # Calculate total processing time
        total_time = sum(event.get('processing_time', 0) or 0 for event in events)
        
        response = {
            'process_id': process_id,
            'file_name': file_name,
            'events': events,
            'total_processing_time': total_time,
            'completed_stages': list(completed_stages),
            'failed_stages': list(failed_stages),
            'pending_stages': [s for s in all_stages if s not in completed_stages and s not in failed_stages],
            'is_completed': len(completed_stages) == len(all_stages),
            'has_failures': len(failed_stages) > 0,
            'current_stage': events[-1]['stage'] if events else None
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        app.logger.error(f"Error getting pipeline status: {str(e)}")
        return jsonify({'error': str(e)}), 500

   
@loader_app.route('/upload', methods=['POST'])
def upload_file():
    print("starting upload file")
    
    start_time = time.time()
    process_id = generate_process_id()  # Generate unique process ID
    set_process_id(process_id)
    try:
        if 'file' in request.files:
            file = request.files['file']
            print("type of file")
            print(type(file))

            if file.filename == '':
                return jsonify({'error': 'No selected file'}), 400

            file_url = load_pdf_into_bucket(file,destination_filename=file.filename,bucket=IMPORT_BUCKET)
            file_name = str(file_url).split('/')[-1]

            processing_time = time.time() - start_time
            log_pipeline_event(
                process_id=process_id,
                file_name=file_name,
                stage=PipelineStage.UPLOAD,
                status=ProcessStatus.COMPLETED,
                processing_time=processing_time,
                metadata={'source': 'file_upload', 'original_filename': file.filename}
            )
            
            return jsonify({
                'message': 'File successfully uploaded', 
                'file_name': file_name,
                'process_id': process_id
            }), 200
        
        elif 'pdf_link' in request.form:
            pdf_link = request.form['pdf_link']
            print("type of pdf_link")
            print(type(pdf_link))

            if pdf_link == '':
                return jsonify({'error': 'No PDF link provided'}), 400

            file_url = load_pdf_link_into_bucket(pdf_link,bucket=IMPORT_BUCKET)
            file_name = str(file_url).split('/')[-1]
            print("filename extra",file_name)
            processing_time = time.time() - start_time
            log_pipeline_event(
                process_id=process_id,
                file_name=file_name,
                stage=PipelineStage.UPLOAD,
                status=ProcessStatus.COMPLETED,
                processing_time=processing_time,
                metadata={'source': 'file_link', 'original_file_url': pdf_link}
            )
            return jsonify({
                'message': 'PDF link successfully uploaded', 
                'file_name': file_name,
                'process_id': process_id
            }), 200
        
        else:
            return jsonify({'error': 'No file or link part'}), 400
    except Exception as e:
        processing_time = time.time() - start_time
        log_pipeline_event(
            process_id=process_id,
            file_name=file.filename if 'file' in locals() else None,
            stage=PipelineStage.UPLOAD,
            status=ProcessStatus.FAILED,
            error_message=str(e),
            processing_time=processing_time
        )
        return jsonify({'error': str(e)}), 500

    
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

@loader_app.route('/view/status/<process_id>')
def view_status(process_id):
    return render_template('status.html', process_id=process_id)