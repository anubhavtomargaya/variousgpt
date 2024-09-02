import os
from pathlib import Path

from flask import jsonify
from google.cloud import storage
from dirs import PDF_DIR
from classify_pdf import classify_pdf_transcript
from db_supabase import insert_classifier_entry

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

IMPORT_BUCKET= 'uploads-mr-pdf'
PROC_PDF_BUCKET = 'pdf-transcripts'
# gcs_client = storage.Client()
gcs_client = storage.Client.from_service_account_json(Path(f'sa_gcs.json'))

def upload_file_to_gcs(file,
                        filename,
                        bucket=None):
    storage_client = gcs_client
    print("uploading file to gcs",file)
    bucket = storage_client.bucket(bucket)
    blob = bucket.blob(filename)
    print("blob",blob)
    blob.upload_from_file(file)
    return blob.public_url


def download_gcs_file_as_bytes(source_blob_name,bucket=None):
    bucket = gcs_client.bucket(bucket)
    blob = bucket.blob(source_blob_name)
    print(blob)
    return blob.download_as_bytes()

def download_gcs_file(source_blob_name, destination_file_name,
                      bucket=None):
    bucket = gcs_client.bucket(bucket)
    blob = bucket.blob(source_blob_name)
    with open(destination_file_name, 'wb') as file_obj:
        blob.download_to_file(file_obj)
    print("file downloaded",destination_file_name)
    return destination_file_name

#utils_main
def download_pdf_from_pdf_bucket_file(file_name,
                                       dir=PDF_DIR,
                                       format='pdf',
                                       bucket=None,
                                       bytes=False,
                                       ):
    
    source_blob_name = _make_file_path(direcotry=dir,file_name=file_name,
                                       local=False,format=format)   
    if bytes:
        return download_gcs_file_as_bytes(source_blob_name=source_blob_name,
                                          bucket=bucket)
    else:
        print("makking tmp path",file_name) 
        destination_file_path = os.path.join('/tmp', f"{file_name}.pdf")
        return download_gcs_file(source_blob_name,
                                 destination_file_name=destination_file_path,
                                 bucket=bucket)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'pdf'

def load_pdf_into_bucket(file,destination_filename,bucket=None):
    try:
        print('loading in bucket',bucket,file)
        print('loading in bucket dest',destination_filename)
        if file:

            filename = Path(destination_filename)
            destination_blob_name = _make_file_path(PDF_DIR,
                                                filename,format='pdf',local=False)
            if not isinstance(file,str):
                file = file
                file_url = upload_file_to_gcs(file, destination_blob_name,bucket=bucket)
            else:
                with open(file,'rb') as tmpfile:
                    file_url = upload_file_to_gcs(tmpfile, destination_blob_name,bucket=bucket)
            return file_url
        else:
            raise Exception("Loaderror",file,allowed_file(destination_filename ))
    except Exception as e:
        raise Exception("LoadError: couldnt upload pdf : %s",e.__str__())
    
## main
def validate_and_classify_pdf(event, context=None):
    print("Processing file")
    if not isinstance(event,dict):
        request_json = event.get_json()
        file_name = request_json['name']
    else:
        file_path = event['name']
        file_name = Path(file_path).name
      
        print(f"Processing file: {file_name} ") #replace with new bucket for pdfs specifically

    try:
        path = download_pdf_from_pdf_bucket_file(file_name=file_name,
                                                bucket=IMPORT_BUCKET)
        classification = classify_pdf_transcript(path)
        if classification:
            print("earning call detected! path:", classification) 
            insert = insert_classifier_entry(import_filename=file_name,given_filename=classification)
            print("inserted",insert)
            url = load_pdf_into_bucket(path,destination_filename=classification,bucket=PROC_PDF_BUCKET)
            # insert = update_classifier_entry(path) # update confirmation for pdf upload
            return jsonify(url)
        else:
            print("earning call NOT detected! response", classification) 
            return jsonify(False )
   
    except Exception as e:
        print("error in processing pdf",e)
        return False
    

if __name__=='__main__':
    f = 'Earnings-Call-Transcript-Q1-FY-2021.pdf'
    def test_download_from_bucket_as_tmp():
        return download_pdf_from_pdf_bucket_file(f)
    
    def test_metadata_service():
        f_path=  download_pdf_from_pdf_bucket_file(f)
        row_id = service_extract_pdf_metadata(f_path)
        return row_id
    
    def test_transcript_extract_service():
        # f_path=  download_pdf_from_pdf_bucket(f)
        f_path=  f
        row_id = service_extract_pdf_metadata(f_path)
        ts_entry = service_extract_transcript_texts(f_path,row_id)
        return ts_entry
    
    def test_process_main():
        bucket_file = 'fy-2024_q1_investor_conference_transcript_raymond_500330.pdf'
        event = { "name":bucket_file,"bucket":'app_bucket'}
        return process_valid_pdf(event)
        
    # print(test_download_from_bucket_as_tmp())
    # print(test_metadata_service())
    # print(test_transcript_extract_service())
    # print(test_process_main())