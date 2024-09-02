
 
from pathlib import Path

from flask import jsonify

from process import service_process_pdf_to_rag

def chunk_embed_valid_pdf(event, context=None):
    print("Processing file")
    if not isinstance(event,dict):
        request_json = event.get_json()
        file_name = request_json['name']
    else:
        file_path = event['name']
        file_name = Path(file_path).name
        # bucket_name = event['bucket']
    try:
        print(f"Processing file: {file_name} in bucket: ")
        return jsonify(service_process_pdf_to_rag(file_name))
    except Exception as e:
        print("error in processing pdf",e)
        return False
    