import json
from pathlib import Path
import openai
from openai import OpenAI
from datetime import datetime
from enum import Enum


BUCKET_NAME = 'gpt-app-data'
class tsFormats(Enum):
    JSON = 'json'
    SRT  = 'srt'
    TXT = 'txt'


def upload_blob_to_gcs_bucket_by_filename(gcs_client,
                            source_filename:Path,
                            source_dir:Path=None,
                            bucket=BUCKET_NAME,
                            format=None,
                            data=None
                            
                              ):
    bucket = gcs_client.bucket(bucket)
    print("FILNEAME",source_filename )
    destination_blob_name = _make_file_path(source_dir,
                                            source_filename,
                                            format=format,
                                            local=False)
    print("DESTBLOB",destination_blob_name)
    blob = bucket.blob(destination_blob_name)
    
    if blob.exists():
        return destination_blob_name
    if not data:
        upload = blob.upload_from_filename(Path(source_dir,f'{source_filename}.{format}').__str__())
    else:
        upload = blob.upload_from_string(str(data))
    print("uploaded:",upload)
    print("gcs name,",destination_blob_name)
    exists = blob.exists()
    print(f"Upload successful: {exists}")
    return destination_blob_name

def transcribe_audio_in_format(client,audio_file_path,
                            format:tsFormats=tsFormats.JSON,
                            prompt="")->openai.types.audio.transcription.Transcription:
    with open(audio_file_path, 'rb') as af:
        print("calling open api whisper started...")
        st = datetime.utcnow()
        transcription = client.audio.transcriptions.create( model= "whisper-1", file=af,
                                                            response_format=format.value,
                                                            prompt=prompt
                                                            )
        print("calling open api end.")
        et = datetime.utcnow()
        total_time = et - st
        print("total processing time ", total_time.seconds, 'seconds')
        print("total cost $", round(0.006*total_time.seconds),2)
    return transcription

def _make_file_path(direcotry:Path,
                    file_name:Path,
                    format:str=None,
                    local=True):
    if not format:
        format = Path(file_name).as_posix().split('.')[-1]
    file_ = f"{Path(file_name).stem}.{format}"
    print("making file path",file_)
    if local:
        return Path(direcotry,file_)
    else:
        parts = direcotry.parts
        if not "data" in parts:
            raise ValueError("DATA DIR not found in path")
        
        data_index = parts.index("data")
        after_data = "/".join(parts[data_index:])

        return f"{after_data}/{file_}"
## setup.nb
CONFIG_FILE='env.json'
def _load_config():
    with open(Path(Path(__file__).parent.resolve(),CONFIG_FILE)) as f:
        return json.load(f)
    
configs = _load_config()
SUPABASE_URL =configs['SUPABASE_URL']
SUPABASE_SERVICE_KEY = configs['SUPABASE_SERVICE_KEY']

def get_openai_key():
    configs = _load_config()
    return configs['OPENAI_KEY']

def get_openai_client():
    client = OpenAI(
        timeout=50.0,
        api_key=get_openai_key())
    return client
    