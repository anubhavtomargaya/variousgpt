
from pathlib import Path
from audio_compress.utils import _make_file_path
from audio_compress.dirs import YOUTUBE_DIR,PROCESSED_DIR
from audio_compress.ffmpeg_compress import preprocess_audio_for_transcription
from google.cloud import storage

BUCKET_NAME = 'gpt-app-data'
gcs_client = storage.Client()

def download_video_file_gcs(file_name,dir=YOUTUBE_DIR)->Path:
    tmp_file_path = _make_file_path(dir,file_name,local=True)
    if tmp_file_path.exists():
        print("tmp exists")
        return tmp_file_path
    src_blob_name = _make_file_path(dir,file_name,local=False)
    bucket = gcs_client.bucket(BUCKET_NAME)
    blob = bucket.blob(src_blob_name)
    print(blob)
    blob.download_to_filename(tmp_file_path)
    return tmp_file_path

def convert_local_path_to_ogg_with_ffmpeg(file_path:Path, output_dir=PROCESSED_DIR):
    output_file = Path(output_dir,f"{file_path.stem}.ogg" )
    print(output_file)
    success = preprocess_audio_for_transcription(file_path, output_file)
    # return Path(output_file) if success else False
    if success:
        bucket = gcs_client.bucket(BUCKET_NAME)
        destination_blob_name = _make_file_path(PROCESSED_DIR,output_file,local=False)
        blob = bucket.blob(destination_blob_name)
        upload = blob.upload_from_filename(output_file)
        print("upload:",upload)
        print("gcs name,",destination_blob_name)
        print("gcs up,",upload)
        exists = blob.exists()
        print(f"Upload successful: {exists}")
        return Path(output_file)
    else:
        False


def process_file(event, context):
    file_name = event['name']
    print(f"Processing file: {file_name}")
    try:
        file_path = download_video_file_gcs(file_name)
        convert_local_path_to_ogg_with_ffmpeg(file_path)
    except Exception as e:
        print(f"Error processing file {file_name}: {e}")