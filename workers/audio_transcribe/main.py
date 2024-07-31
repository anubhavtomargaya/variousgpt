


from pathlib import Path
from preproc import service_audio_to_gcs_transcript

def transcribe_audio_file(event, context=None):
    if not isinstance(event,dict):
        request_json = event.get_json()
        file_name = request_json['name']
    else:
        file_path = event['name']
        file_name = Path(file_path).name
    # bucket_name = event['bucket']
    # print(f"Processing file: {file_name} in sbucket: {bucket_name}")
    return service_audio_to_gcs_transcript(file_name)