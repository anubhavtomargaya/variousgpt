from flask import Blueprint, jsonify, request, render_template
from datetime import datetime
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from enum import Enum
import json
from gpt_app.common.supabase_handler import supabase as supabase_client

loader_bp = Blueprint('gflow', __name__, url_prefix='/gflow')

class PipelineStage(str, Enum):
    UPLOAD = 'upload'
    CLASSIFICATION = 'classification'
    METADATA = 'metadata'
    TS_EXTRACTION = 'text_extraction'
    QA_GENERATION = 'qa_generation'
    QA_MG_INTEL_GENERATION = 'intel_generation'
    EMBEDDING_GENERATION = 'embedding_generation'

class ProcessStatus(str, Enum):
    COMPLETED = 'completed'
    FAILED = 'failed'
    STARTED = 'started'

@dataclass
class PipelineLog:
    id: str
    created_at: str
    process_id: str
    stage: PipelineStage
    status: ProcessStatus
    file_name: str
    user_email: str
    error_message: Optional[str]
    metadata: Dict[str, Any]
    processing_time: Optional[float]

class PipelineLogRepository:
    def __init__(self, supabase_client):
        self.client = supabase_client
        self.table = 'pipeline_events'

    def get_all_processes(self) -> List[Dict[str, Any]]:
        """Get unique process IDs with their latest status and filename"""
        try:
            response = (self.client
                       .table(self.table)
                       .select('process_id, file_name, status, created_at')
                       .order('created_at', desc=True)
                       .execute())
            
            # Get unique processes with their latest status
            processes = {}
            for record in response.data:
                if record['process_id'] not in processes:
                    processes[record['process_id']] = {
                        'process_id': record['process_id'],
                        'file_name': record['file_name'],
                        'latest_status': record['status'],
                        'created_at': record['created_at']
                    }
            
            return list(processes.values())
        except Exception as e:
            print(f"Error fetching processes: {str(e)}")
            return []

    def get_all_stages(self) -> List[str]:
        """Get all possible stages"""
        return [stage.value for stage in PipelineStage]

    def get_logs_by_process(self, process_id: str) -> List[Dict[str, Any]]:
        """Get all logs for a specific process"""
        try:
            response = (self.client
                       .table(self.table)
                       .select('*')
                       .eq('process_id', process_id)
                       .order('created_at', desc=True)
                       .execute())
            return response.data
        except Exception as e:
            print(f"Error fetching logs for process {process_id}: {str(e)}")
            return []

    def get_logs_filtered(
        self,
        process_ids: Optional[List[str]] = None,
        stages: Optional[List[str]] = None,
        status: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """Get logs with various filters"""
        try:
            query = self.client.table(self.table).select('*')

            # Apply filters
            if process_ids:
                query = query.in_('process_id', process_ids)
            if stages:
                query = query.in_('stage', stages)
            if status:
                query = query.eq('status', status)
            if from_date:
                query = query.gte('created_at', from_date)
            if to_date:
                query = query.lte('created_at', to_date)

            # Calculate pagination
            start = (page - 1) * page_size
            end = start + page_size

            # Get total count for pagination
            count_response = query.count().execute()
            total_count = count_response.count if count_response else 0

            # Get paginated results
            response = (query
                       .order('created_at', desc=True)
                       .range(start, end - 1)
                       .execute())

            return {
                'data': response.data,
                'page': page,
                'page_size': page_size,
                'total_count': total_count,
                'total_pages': (total_count + page_size - 1) // page_size
            }
        except Exception as e:
            print(f"Error fetching filtered logs: {str(e)}")
            return {
                'data': [],
                'page': page,
                'page_size': page_size,
                'total_count': 0,
                'total_pages': 0
            }

    def get_process_summary(self, process_id: str) -> Dict[str, Any]:
        """Get summary statistics for a process"""
        try:
            response = (self.client
                       .table(self.table)
                       .select('*')
                       .eq('process_id', process_id)
                       .execute())
            
            logs = response.data
            if not logs:
                return {}

            stages_completed = sum(1 for log in logs if log['status'] == ProcessStatus.COMPLETED.value)
            stages_failed = sum(1 for log in logs if log['status'] == ProcessStatus.FAILED.value)
            total_processing_time = sum(log.get('processing_time', 0) or 0 for log in logs)
            
            # Get timestamps
            timestamps = [datetime.fromisoformat(log['created_at'].replace('Z', '+00:00')) 
                        for log in logs]
            
            return {
                'process_id': process_id,
                'file_name': logs[0]['file_name'],
                'total_stages': len(logs),
                'completed_stages': stages_completed,
                'failed_stages': stages_failed,
                'total_processing_time': total_processing_time,
                'start_time': min(timestamps).isoformat(),
                'end_time': max(timestamps).isoformat(),
                'stages': sorted(set(log['stage'] for log in logs)),
                'current_status': logs[0]['status']  # Latest status
            }
        except Exception as e:
            print(f"Error fetching summary for process {process_id}: {str(e)}")
            return {}

# Initialize repository
repo = PipelineLogRepository(supabase_client)

# API Routes
@loader_bp.route('/processes', methods=['GET'])
def get_processes():
    """Get list of processes with their latest status"""
    processes = repo.get_all_processes()
    return jsonify(processes)

@loader_bp.route('/stages', methods=['GET'])
def get_stages():
    """Get list of possible stages"""
    stages = repo.get_all_stages()
    return jsonify(stages)

@loader_bp.route('/process/<process_id>', methods=['GET'])
def get_process_logs(process_id):
    """Get all logs for a specific process"""
    logs = repo.get_logs_by_process(process_id)
    return jsonify(logs)

@loader_bp.route('/process/<process_id>/summary', methods=['GET'])
def get_process_summary(process_id):
    """Get summary for a specific process"""
    summary = repo.get_process_summary(process_id)
    return jsonify(summary)

@loader_bp.route('/logs', methods=['GET'])
def get_logs():
    """Get filtered logs"""
    process_ids = request.args.getlist('process_id')
    stages = request.args.getlist('stage')
    status = request.args.get('status')
    from_date = request.args.get('from_date')
    to_date = request.args.get('to_date')
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 20))

    result = repo.get_logs_filtered(
        process_ids=process_ids if process_ids else None,
        stages=stages if stages else None,
        status=status,
        from_date=from_date,
        to_date=to_date,
        page=page,
        page_size=page_size
    )
    return jsonify(result)

@loader_bp.route('/', methods=['GET'])
def index():
    """Main dashboard view"""
    initial_data = {
        'processes': repo.get_all_processes(),
        'stages': repo.get_all_stages(),
        'statuses': [status.value for status in ProcessStatus]
    }
    return render_template('loader/index.html', initial_data=initial_data)
# Error handlers
@loader_bp.errorhandler(404)
def not_found_error(error):
    return jsonify({"error": "Resource not found"}), 404

@loader_bp.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500