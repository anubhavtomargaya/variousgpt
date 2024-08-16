import os
from pathlib import Path
import requests

from google.cloud import storage
from extract_pdf_metadata import service_extract_pdf_metadata
from process_pdf_text import service_extract_transcript_texts
from dirs import PDF_DIR

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
BUCKET_NAME = 'pdf-transcripts'
# gcs_client = storage.Client()
gcs_client = storage.Client.from_service_account_json(Path(f'sa_gcs.json'))

def download_gcs_file_as_bytes(source_blob_name):
    bucket = gcs_client.bucket(BUCKET_NAME)
    blob = bucket.blob(source_blob_name)
    print(blob)
    return blob.download_as_bytes()

def download_gcs_file(source_blob_name, destination_file_name):
    bucket = gcs_client.bucket(BUCKET_NAME)
    blob = bucket.blob(source_blob_name)
    with open(destination_file_name, 'wb') as file_obj:
        blob.download_to_file(file_obj)
    print("file downloaded",destination_file_name)
    return destination_file_name

def download_pdf_from_pdf_bucket(file_name, dir=PDF_DIR,format='pdf',bytes=False):
    source_blob_name = _make_file_path(direcotry=dir,file_name=file_name,
                                       local=False,format=format)   
    if bytes:
        return download_gcs_file_as_bytes(source_blob_name=source_blob_name)
    else:
        destination_file_path = os.path.join('/tmp', file_name)
        return download_gcs_file(source_blob_name,destination_file_name=destination_file_path)
    
def process_stage_one(file_name):
    fname = download_pdf_from_pdf_bucket(file_name)
    try:
        row_id = service_extract_pdf_metadata(fname)
        if row_id:
            final_ = service_extract_transcript_texts(fname,row_id)
            print("final donw")
            print(final_)
            return row_id
    except Exception as e:
        print("error in processing pdf",e)
        return False

def process_qa_mg_intel(filename):
    url = "https://asia-southeast1-gmailapi-test-361320.cloudfunctions.net/process_qa_mg_intel_http"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "name": filename
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        return response.json() 
    else:
        print("msg",{"error": f"Request failed with status code {response.status_code}"})
        return False




def process_valid_pdf(event, context=None):
    print("Processing file")
    if not isinstance(event,dict):
        request_json = event.get_json()
        file_name = request_json['name']
    else:
        file_path = event['name']
        file_name = Path(file_path).name
        bucket_name = event['bucket']
        print(f"Processing file: {file_name} in bucket: {bucket_name}")
    pdf_to_ts = process_stage_one(file_name)
    if not pdf_to_ts:
        raise Exception("unable to process stage one %s",pdf_to_ts)
    print('processed pdf to ts ')
    ts_intel = process_qa_mg_intel(file_name)

    print("ts intel output",ts_intel)
    return ts_intel

if __name__=='__main__':
    f = 'Earnings-Call-Transcript-Q1-FY-2021.pdf'
    def test_download_from_bucket_as_tmp():
        return download_pdf_from_pdf_bucket(f)
    
    def test_metadata_service():
        f_path=  download_pdf_from_pdf_bucket(f)
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
    print(test_process_main())