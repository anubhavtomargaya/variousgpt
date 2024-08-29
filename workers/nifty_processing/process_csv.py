import os
from pathlib import Path

from google.cloud import storage
from dirs import DATA_DIR



#utils.py
def _make_file_path(direcotry:Path,
                    file_name:Path,
                    format:str=None,
                    local=True):
    if not format:
        format = Path(file_name).as_posix().split('.')[-1]
    file_ = f"{Path(file_name).stem}.{format}"
    if local:
        return Path(direcotry,file_)
    else:
        parts = direcotry.parts
        if not "data" in parts:
            raise ValueError("DATA DIR not found in path")
        
        data_index = parts.index("data")
        after_data = "/".join(parts[data_index:])

        return f"{after_data}/{file_}"

#consts.py
APP_BUCKET = 'gpt-app-data'
BUCKET_NAME = 'nifty-data'
# gcs_client = storage.Client()
gcs_client = storage.Client.from_service_account_json(Path(f'sa_gcs.json'))

def download_gcs_file_as_bytes(source_blob_name):
    bucket = gcs_client.bucket(BUCKET_NAME)
    blob = bucket.blob(source_blob_name)
    print(blob)
    return blob.download_as_bytes()

def download_gcs_file(source_blob_name, destination_file_name,bucket=BUCKET_NAME):
    bucket = gcs_client.bucket(BUCKET_NAME)
    blob = bucket.blob(source_blob_name)
    with open(destination_file_name, 'wb') as file_obj:
        blob.download_to_file(file_obj)
    print("file downloaded",destination_file_name)
    return destination_file_name

def download_csv_from_bucket(file_name, dir=DATA_DIR,format='csv',bytes=False,bucket=None):
    source_blob_name = _make_file_path(direcotry=dir,file_name=file_name,
                                       local=False,format=format)   
    if bytes:
        return download_gcs_file_as_bytes(source_blob_name=source_blob_name)
    else:
        print("makking tmp path",file_name) 
        destination_file_path = os.path.join('/tmp', f"{file_name}")
        return download_gcs_file(source_blob_name,destination_file_name=destination_file_path,bucket=bucket)

