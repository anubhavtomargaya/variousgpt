

from gpt_app.common.utils_dir import _make_file_path
from  gpt_app.blueprints.gptube.load_pdf import download_pdf_from_bucket, download_pdf_from_pdf_bucket_file, download_transcript_json_from_bucket
from  gpt_app.blueprints.gptube.helpers_pdf import extract_text_from_pdf_bytes
from  gpt_app.blueprints.gptube.helpers_db import create_doc_for_file
from  gpt_app.blueprints.gptube.classify_pdf import classify_pdf_transcript
from gpt_app.common.utils_text import split_document, count_words,generate_hash_key
from gpt_app.common.supabase_handler import check_tdoc_exist, insert_chunk_doc_entry, insert_classifier_entry
from gpt_app.blueprints.gptube.process_pdf_text import service_extract_transcript_texts

import json
CHUNK_PARAMS  = (2000,100)

APP_BUCKET = 'gpt-app-data'
PROC_PDF_BUCKET = 'pdf-transcripts'

def get_pdf_txt(file):
    bdata = download_pdf_from_bucket(file,bucket=APP_BUCKET)
    txt = extract_text_from_pdf_bytes(bdata)
    print('text')
    # print(txt)
    return txt 

# def validate_earnings_transcript(import_file_name):
#     path = download_pdf_from_pdf_bucket_file(file_name=import_file_name,
#                                              bucket=APP_BUCKET)
#     classificaiton = classify_pdf_transcript(path)
#     if classificaiton:
#         print("earning call detected! path:", classificaiton) 
#         return classificaiton
#     else:
#         print("earning call NOT detected! response", classificaiton) 
#         return False 


def get_transcript_text(file):
    print("file")
    print(file)
    bdata = download_transcript_json_from_bucket(file)
    print('text')
    print(bdata)
    txt = json.loads(bdata)
    txt_ = txt['text']
    # txt = extract_text_from_pdf_bytes(bdata)
    print(txt_)
    return txt_
from .load_pdf import load_pdf_into_bucket 


def process_pdf_input_v2(file_name,
                         bucket=APP_BUCKET):
    ## proc I 
        # download pdf from app bucket 
        # classify pdf transcript - get file name 
        # - make sure consistent to avoid dups
        # insert entry 
        # dump file to new bucket 
    # return new file path / meta

    ## part 2 
    # download from proc bucket 
    # metadata 
    # diarized text 
    # level 1 intel
    # level 2 intel
    pass 
import requests

def run_classifier(name):
    url = "https://asia-southeast1-gmailapi-test-361320.cloudfunctions.net/gen1_classify_upload_pdf"
    headers = {"Content-Type": "application/json"}
    data = {"name": name}

    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        return response.json()  # Assuming the response is in JSON format
    else:
        return {"error": response.status_code, "message": response.text}



def process_pdf_to_doc(file,added_by=None):
    # tdoc = check_tdoc_exist(file)
    # if  tdoc:
    #     return False
    # else:

    #     path = download_pdf_from_pdf_bucket_file(file_name=file,
    #                                          bucket=APP_BUCKET)
    #     classificaiton = classify_pdf_transcript(path)
    #     if classificaiton:
    #         print("earning call detected! path:", classificaiton) 
    #         # return classificaiton
    #         insert = insert_classifier_entry(import_filename=file,given_filename=classificaiton)
    #         print("inserted",insert)
    #     else:
    #         print("earning call NOT detected! response", classificaiton) 
    #         return False 
    classification = run_classifier(file)
    if classification:
        # txt = get_pdf_txt(file)
        # print("fileeee",file)
        # meta = {'chunk_params':CHUNK_PARAMS}
        # chunks = split_document(txt,CHUNK_PARAMS[0],CHUNK_PARAMS[1])
        # doc = create_doc_for_file(chunks=chunks,
        #                         filename=classification,
        #                         e='pdf',
        #                         meta=meta)
       
        # try:

        #     sp = insert_chunk_doc_entry(doc=doc,added_by=added_by)
        #     print(sp)
        # except Exception as e:
        #     print("already exists?",e)

        return {"url":classification,
                }
    else:
        return {"url":"Unsuitable Document"}


if __name__=='__main__':
    f = 'Investors-call-transcript-for-Q4-FY-2023-24.pdf'

    def test_download():
        return download_pdf_from_bucket(f)
    
    def test_mupdf_text():
        bdata = download_pdf_from_bucket(f)
        return extract_text_from_pdf_bytes(bdata)
    
    def test_split_text():
        bdata = download_pdf_from_bucket(f)
        txt = extract_text_from_pdf_bytes(bdata)
        return split_document(txt,1000,100)
    
    def test_create_doc():
        bdata = download_pdf_from_bucket(f)
        txt = extract_text_from_pdf_bytes(bdata)
        chunks = split_document(txt,1000,100)
        return create_doc_for_file(filename=f,chunks=chunks)
    
    def test_process():
        return process_pdf_to_doc(f)
    
    # print(test_download())
    # print(test_mupdf_text())
    # print(test_split_text())
    print(test_process())
    # print(test_create_doc())