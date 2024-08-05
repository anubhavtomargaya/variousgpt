
from pathlib import Path
from utils_em import _make_file_path, get_openai_client
from dirs import *
from google.cloud import storage
# BUCKET_NAME = 'gpt-app-data'
BUCKET_NAME = 'pdf-transcripts'
client = get_openai_client()
TMP_DIR = Path('/tmp')
BUCKET_NAME = 'gpt-app-data'

# gcs_client = storage.Client()
gcs_client = storage.Client.from_service_account_json(Path(f'sa_gcs.json'))

def upload_file_to_gcs(file,
                        filename,
                        bucket=BUCKET_NAME):
    storage_client = gcs_client
    print("uploading file to gcs",file)
    bucket = storage_client.bucket(bucket)
    blob = bucket.blob(filename)
    print("blob",blob)
    blob.upload_from_file(file)
    return blob.public_url

def download_gcs_file(source_blob_name, destination_file_name,bucket=BUCKET_NAME):
    bucket = gcs_client.bucket(bucket)
    blob = bucket.blob(source_blob_name)
    with open(destination_file_name, 'wb') as file_obj:
        blob.download_to_file(file_obj)
    print("file downloaded",destination_file_name)
    return destination_file_name

def download_gcs_file_as_bytes(source_blob_name,bucket=None):
    bucket = gcs_client.bucket(bucket)
    blob = bucket.blob(source_blob_name)
    print(blob)
    return blob.download_as_bytes()

def download_pdf_from_bucket(file_name, dir=PDF_DIR,format='pdf',bucket=None):
    source_blob_name = _make_file_path(direcotry=dir,file_name=file_name,
                                       local=False,format=format)   
 
    return download_gcs_file_as_bytes(source_blob_name=source_blob_name,bucket=bucket)

def load_pdf_into_bucket(file,destination_filename,bucket=None):
    try:
        print('loading in bucket',bucket,file)
        print('loading in bucket dest',destination_filename)
        if file:
            filename = Path(destination_filename)
            destination_blob_name = _make_file_path(PDF_DIR,
                                                filename,format='pdf',local=False)
            with open(file,'rb') as tmpfile:
                file_url = upload_file_to_gcs(tmpfile, destination_blob_name,bucket=bucket)
                return file_url
        else:
            raise Exception("Loaderror",file,destination_filename )
    except Exception as e:
        raise Exception("LoadError: couldnt upload pdf : %s",e.__str__())
    
def download_pdf_from_pdf_bucket_file(file_name, dir=PDF_DIR,format='pdf',bytes=False,bucket=None):
    source_blob_name = _make_file_path(direcotry=dir,file_name=file_name,
                                    local=False,format=format)   
    if bytes:
        return download_gcs_file_as_bytes(source_blob_name=source_blob_name)
    else:
        print("makking tmp path",file_name) 
        destination_file_path = os.path.join('/tmp', f"{file_name}.pdf")
        return download_gcs_file(source_blob_name,destination_file_name=destination_file_path,bucket=bucket)
        