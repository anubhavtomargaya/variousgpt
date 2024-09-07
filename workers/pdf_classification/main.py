import os
from pathlib import Path

from flask import jsonify
from google.cloud import storage
from dirs import PDF_DIR
from classify_pdf import classify_pdf_transcript
from db_supabase import check_pdf_exist, insert_classifier_entry, insert_initial_transcript_entry

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

def build_file_name(metadata):
    keys = ['financial_year','quarter','company_name','doc_type','nse_scrip_code']

def process_concall_metadata():pass 

def insert_metadata_entry(metadata):

    try:

        check_request = {
                            "company_name":metadata['company_name'],
                            "doc_type":metadata['doc_type'],
                            "financial_year":metadata['financial_year'],
                            "quarter":metadata['quarter'],
                        }
        existing= check_pdf_exist(**check_request)

        if not existing:
            entry = {
                    "company_name":metadata['company_name'],
                    "date":metadata['date'],
                    "quarter":metadata['quarter'],
                    "file_name":metadata['doc_name'],
                    "financial_year":metadata['financial_year'],
                    "doc_type":metadata['doc_type'],
                    "description":metadata['description'],
                    "key_people":metadata['key_people'],
                    "ticker":f"{metadata['nse_scrip_code']}",
                    }
            row_id = insert_initial_transcript_entry(**entry)
            print("new row id",row_id)
            return row_id
        else:
            print("already esits",existing)
            return True
    except Exception as e:
        print("Excep,",e)
        return False


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
        classifcation = None
        path = download_pdf_from_pdf_bucket_file(file_name=file_name,
                                                bucket=IMPORT_BUCKET)
        metadata = classify_pdf_transcript(path)
        if len(metadata.keys())<1:
            classifcation = False
        else:
            classifcation = True

        if classifcation:
            f_name_new = metadata.get('doc_name',None)
            if not file_name:
                raise Exception("file name not found in response")
            print("earning call detected! path:", metadata) 
            insert = insert_classifier_entry(import_filename=file_name,given_filename=f_name_new)
            if not insert:
                raise Exception("classification error")
            
            url = load_pdf_into_bucket(path,destination_filename=f_name_new,bucket=PROC_PDF_BUCKET)
            print("inserted",insert)
            if not url:
                raise Exception("Error uploading to bucket")
            
            metadata['addn_meta']  = { }
            insert_meta = insert_metadata_entry(metadata)
            if not insert_meta:
                raise Exception("Problem inserting metadata")
            print("inserted",insert_meta )
            # insert = update_classifier_entry(path) # update confirmation for pdf upload
            return jsonify(url)
        else:
            print("earning call NOT detected! response", metadata) 
            return jsonify(False )
   
    except Exception as e:
        print("error in processing pdf",e)
        return  jsonify(False )
    

if __name__=='__main__':
    # f = 'Earnings-Call-Transcript-Q1-FY-2021.pdf'
    f= 'CC-Jun23.pdf'
    # f = 'fy-2024_q1_investor_conference_transcript_raymond_500330.pdf'
    def test_download_from_bucket_as_tmp():
        return download_pdf_from_pdf_bucket_file(f)
    
    def test_metadata_service():
        f_path=  download_pdf_from_pdf_bucket_file(f,bucket=APP_BUCKET)
        return classify_pdf_transcript(f_path)
    
    def test_metadata_entry():
        f_path=  Path(download_pdf_from_pdf_bucket_file(f,bucket=APP_BUCKET))
        
        metadata =  classify_pdf_transcript(f_path)
        f_new = metadata['doc_name']
        insert_clf = insert_classifier_entry(import_filename=f_path.name,given_filename=f_new)
        insert_meta = insert_metadata_entry(metadata)
        print("inserted_new",insert_clf,"insert_meta" ,insert_meta
              )
        return insert_meta
        
    
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
    print(test_metadata_entry())
    # print(test_transcript_extract_service())
    # print(test_process_main())