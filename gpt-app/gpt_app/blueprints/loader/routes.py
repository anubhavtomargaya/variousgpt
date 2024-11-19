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
            log_pipeline_event(
                process_id=process_id,
                file_name=file_name if file_name else ' ',
                stage=PipelineStage.UPLOAD,
                status=ProcessStatus.STARTED,
                metadata={'source': 'file_upload', 'original_filename': file.filename}
            )

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
            log_pipeline_event(
                process_id=process_id,
                file_name=file_name if file_name else ' ',
                stage=PipelineStage.UPLOAD,
                status=ProcessStatus.STARTED,
               metadata={'source': 'file_link', 'original_file_url': pdf_link}
            )
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
def process_pdf():
    start_time = time.time()
    process_id = generate_process_id()
    
    if not is_logged_in():
        print('not logged in!')
        # redirect(url_for('google_auth.login'))
        
    try:
        mthd = request.method 
        args = request.args
        app.logger.info('method: %s', mthd)
        app.logger.info('args: %s', args)
        
        if mthd == 'GET':
            file = args.get('file')
        elif mthd == 'POST':
            data = request.get_json()
            file = data.get('file')
        else:
            raise HTTPException("Invalid Method")

        if not file:
            raise HTTPException("file not provided")
            
        print(file, 'file')
        result = process_pdf_to_doc(file=file, added_by=get_user_email())
        
       
        result['process_id'] = process_id
        result['file_url'] = file
       
        return jsonify(result)
        
    except Exception as e:
        # Log failure
        processing_time = time.time() - start_time
        log_pipeline_event(
            process_id=process_id,
            file_name=file.split('/')[-1] if 'file' in locals() else 'unknown',
            stage=PipelineStage.UPLOAD,
            status=ProcessStatus.FAILED,
            error_message=str(e),
            processing_time=processing_time,
            metadata={'source': 'pdf_link'}
        )
        return jsonify({'error': str(e)}), 500

@loader_app.route('/status/<process_id>', methods=['GET'])
def get_pipeline_status(process_id):
    """Get current status of the process"""
    try:
        events = get_pipeline_events(process_id)
        
        if not events:
            return jsonify({'error': 'No events found for this process'}), 404
            
        file_name = events[0]['file_name']
        original_url = events[0].get('metadata', {}).get('original_file_url')
        
        # All possible stages in order
        all_stages = [
            'upload',
            'classification',
            # 'metadata',
            'text_extraction',
            'summary',
            'guidance',
            'tags',
            'extra',
            'takeaway',
            'qa_generation',
            'intel_generation',
            # 'embedding_generation'
        ]
        
        # Get stages by status
        completed_stages = {
            event['stage'] for event in events 
            if event['status'] == 'completed'
        }
        failed_stages = {
            event['stage'] for event in events 
            if event['status'] == 'failed'
        }
        in_progress_stages = {
            event['stage'] for event in events 
            if event['status'] == 'started'
        }
        
        # Calculate total processing time
        total_time = sum(event.get('processing_time', 0) or 0 for event in events)
        
        # Get current stage details
        current_event = events[-1] if events else None
        current_stage = current_event['stage'] if current_event else None
        current_stage_status = current_event['status'] if current_event else None
        
        # Get stage-wise status and times
        stage_details = {}
        for stage in all_stages:
            stage_events = [e for e in events if e['stage'] == stage]
            if stage_events:
                latest_event = stage_events[-1]
                stage_details[stage] = {
                    'status': latest_event['status'],
                    'processing_time': latest_event.get('processing_time', 0),
                    'error_message': latest_event.get('error_message'),
                    'started_at': latest_event['created_at'],
                    'metadata': latest_event.get('metadata', {})
                }
            else:
                stage_details[stage] = {
                    'status': 'pending',
                    'processing_time': 0,
                    'error_message': None,
                    'started_at': None,
                    'metadata': {}
                }
        
        response = {
            'process_id': process_id,
            'file_name': file_name,
            'file_url': original_url,
            'events': events,
            'total_processing_time': round(total_time, 2),
            'completed_stages': list(completed_stages),
            'failed_stages': list(failed_stages),
            'in_progress_stages': list(in_progress_stages),
            'pending_stages': [s for s in all_stages if s not in completed_stages | failed_stages | in_progress_stages],
            'is_completed': len(completed_stages) == len(all_stages),
            'has_failures': len(failed_stages) > 0,
            'is_processing': len(in_progress_stages) > 0,
            'current_stage': current_stage,
            'current_stage_status': current_stage_status,
            'stage_details': stage_details,
            'progress_percentage': round((len(completed_stages) / len(all_stages)) * 100, 1),
            'all_stages': all_stages  # Include for reference
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        app.logger.error(f"Error getting pipeline status: {str(e)}")
        return jsonify({'error': str(e)}), 500

@loader_app.route('/view/status/<process_id>')
def view_status(process_id):
    """Render status page"""
    try:
        status_response = get_pipeline_status(process_id)
        initial_status = status_response[0].json if status_response[1] == 200 else {}
        
        return render_template(
            'status.html',
            process_id=process_id,
            initial_status=initial_status,
            refresh_interval=7000  # Poll every 2 seconds
        )
    except Exception as e:
        app.logger.error(f"Error rendering status page: {str(e)}")
        return render_template(
            'status.html',
            process_id=process_id,
            initial_status={},
            refresh_interval=7000
        )