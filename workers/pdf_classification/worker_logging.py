from enum import Enum
from datetime import datetime
import random
import string
import time
from typing import Optional, Dict, Any

from db_supabase import supabase_insert

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


def generate_process_id():
    """Generate a unique process ID with timestamp prefix"""
    # Get current date in MMDD format
    timestamp = datetime.now().strftime('%m%d')
    
    # Generate 6 random alphanumeric characters
    chars = string.ascii_letters + string.digits
    random_str = ''.join(random.choices(chars, k=6))
    
    # Combine with 'p' prefix
    return f"p{timestamp}{random_str}"  # e.g., p1025ABC123

def log_pipeline_event(
    process_id: str,
    file_name: str,
    stage: PipelineStage,
    status: ProcessStatus,
    error_message: Optional[str] = None,
    processing_time: Optional[float] = None,
    metadata: Optional[Dict[str, Any]] = None
):
    """Log a pipeline event"""
    try:
        data = {
            'process_id': process_id,
            'file_name': file_name,
            'stage': stage,
            'status': status,
            'user_email': 'getstockrabit@gmail.com'
        }
        
        if error_message:
            data['error_message'] = error_message
        if processing_time:
            data['processing_time'] = processing_time
        if metadata:
            data['metadata'] = metadata

        return supabase_insert('pipeline_events',data)
    except Exception as e:
        print(f"Error logging pipeline event: {str(e)}")
        return None