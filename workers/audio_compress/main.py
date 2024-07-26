from flask import Request, jsonify
from pathlib import Path
from google.cloud import storage
from .utils import _make_file_path
from .dirs import YOUTUBE_DIR, PROCESSED_DIR
from .ffmpeg_compress import preprocess_audio_for_transcription

BUCKET_NAME = 'gpt-app-data'
SRC_BUCKET = 'youtube-bucket-audio'
gcs_client = storage.Client()

def download_video_file_gcs(file_name, dir=YOUTUBE_DIR) -> Path:
    # Use /tmp directory for temporary storage
    tmp_dir = Path('/tmp')
    tmp_file_path = Path(tmp_dir,file_name)
    if tmp_file_path.exists():
        print("tmp exists")
        return tmp_file_path
    src_blob_name = _make_file_path(dir, file_name, local=False)
    bucket = gcs_client.bucket(SRC_BUCKET)
    blob = bucket.blob(src_blob_name)
    print(blob)
    print("down to ", tmp_file_path)
    blob.download_to_filename(tmp_file_path)
    return tmp_file_path

def convert_local_path_to_ogg_with_ffmpeg(file_path: Path, output_dir=PROCESSED_DIR):
    output_file = Path('/tmp', f"{file_path.stem}.ogg")
    print(output_file)
    success = preprocess_audio_for_transcription(file_path, output_file)
    if success:
        bucket = gcs_client.bucket(BUCKET_NAME)
        destination_blob_name = _make_file_path(PROCESSED_DIR, output_file.name, local=False)
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_filename(output_file)
        exists = blob.exists()
        print(f"Upload successful: {exists}")
        return Path(output_file)
    else:
        return False

def process_file(event, context=None):
    print("Processing file")
    if not isinstance(event,dict):
        request_json = event.get_json()
        file_name = request_json['name']
    else:
        file_path = event['name']
        file_name = Path(file_path).name
        bucket_name = event['bucket']
        print(f"Processing file: {file_name} in bucket: {bucket_name}")

    try:
        file_path = download_video_file_gcs(file_name)
        optah =  convert_local_path_to_ogg_with_ffmpeg(file_path)
        return jsonify(optah.name) if optah else jsonify(False), 200

    except Exception as e:


        print(f"Error processing file {file_name}: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500
