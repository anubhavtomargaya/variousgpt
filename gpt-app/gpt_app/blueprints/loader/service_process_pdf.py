
import time
from  gpt_app.blueprints.loader.load_pdf import download_pdf_from_bucket
from  gpt_app.blueprints.loader.helpers_pdf import extract_text_from_pdf_bytes
from  gpt_app.blueprints.loader.helpers_db import create_doc_for_file

CHUNK_PARAMS  = (2000,100)

APP_BUCKET = 'gpt-app-data'
PROC_PDF_BUCKET = 'pdf-transcripts'

def get_pdf_txt(file):
    bdata = download_pdf_from_bucket(file,bucket=APP_BUCKET)
    txt = extract_text_from_pdf_bytes(bdata)
    print('text')
    # print(txt)
    return txt 

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

def run_classifier(name,process_id):
    url = "https://asia-southeast1-gmailapi-test-361320.cloudfunctions.net/process_classify_pdf_metadata"
    headers = {"Content-Type": "application/json"}
    data = {"name": name,'process_id':process_id}
    print("url",url)
    response = requests.post(url, headers=headers, json=data)
    print("response clasifer", response.__dict__)
    if response.status_code == 200:
        return response.json()  # Assuming the response is in JSON format
    else:
        return {"error": response.status_code, "message": response.text}


def run_extract_pdf_transcript(name,process_id):
    # start_time = time.time()
    try:

        # url = "https://asia-southeast1-gmailapi-test-361320.cloudfunctions.net/process_pdf_transcript_intel"
        url = "https://asia-southeast1-gmailapi-test-361320.cloudfunctions.net/process_pdf_extract_main_http"
        headers = {"Content-Type": "application/json"}
        data = {"name": name,'process_id':process_id}
        # log_pipeline_event(
        #     file_name=name,
        #     process_id=process_id,
        #     stage=PipelineStage.TS_EXTRACTION,
        #     status=ProcessStatus.STARTED,
        # )
        response = requests.post(url, headers=headers, json=data)
        print("response extact", response.__dict__)
        data = response.json()
        if response.status_code == 200:
            # processing_time = time.time() - start_time
            # log_pipeline_event(
            #     file_name=name,
            #     process_id=process_id,
            #     stage=PipelineStage.TS_EXTRACTION,
            #     status=ProcessStatus.COMPLETED,
            #     processing_time=processing_time,
            #     metadata=data
            # )
            return response.json()  # Assuming the response is in JSON format
        else:
            return {"error": response.status_code, "message": response.text}
    except Exception as e:
        # processing_time = time.time() - start_time
        # log_pipeline_event(
        #     file_name=name ,
        #     process_id=process_id,
        #     stage=PipelineStage.TS_EXTRACTION,
        #     status=ProcessStatus.FAILED,
        #     error_message=str(e),
        #     processing_time=processing_time
        # )
        return {"error": "fatal", "message": str(e)}



from  gpt_app.blueprints.loader.worker_logging import log_pipeline_event,PipelineStage,ProcessStatus
from  gpt_app.common.session_manager import get_process_id

def process_pdf_to_doc(file,added_by=None):
     
    start_time = time.time()
    process_id = get_process_id()
    if not process_id:
        print("No process_id found in session")
        return {"error": "Process ID not found"}

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
    try:
        # log_pipeline_event(
        #     file_name=file,
        #     process_id=process_id,
        #     stage=PipelineStage.CLASSIFICATION,
        #     status=ProcessStatus.STARTED,
        # )
        classification = run_classifier(file,process_id)
        if not classification:
            raise Exception("ClassifierError: Returned None",classification)
        # processing_time = time.time() - start_time
        # log_pipeline_event(
        #     file_name=file,
        #     process_id=process_id,
        #     stage=PipelineStage.CLASSIFICATION,
        #     status=ProcessStatus.COMPLETED,
        #     processing_time=processing_time,
        #     metadata={'valid':None}
        # )
        # file_name = json.loads(classification).__dict__['_content']
        print('classf',classification)
        print('file name',classification.split('/')[-1])
    except Exception as e:
        # processing_time = time.time() - start_time
        # log_pipeline_event(
        #     file_name=file,
        #     process_id=process_id,
        #     stage=PipelineStage.CLASSIFICATION,
        #     status=ProcessStatus.FAILED,
        #     error_message=str(e),
        #     processing_time=processing_time
        # )
        print("error in classifying pdf",e)

    if classification:
        
        extract_transcript = run_extract_pdf_transcript(classification.split('/')[-1],
                                                        process_id=process_id)
        if extract_transcript:

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
            print('url',classification)
            print('etc',extract_transcript)
            return {"url":classification,
                    "etc":extract_transcript
                    }
        else:
        #     processing_time = time.time() - start_time
        #     log_pipeline_event(
        #     file_name=file,
        #     process_id=process_id,
        #     stage=PipelineStage.TS_EXTRACTION,
        #     status=ProcessStatus.FAILED,
        #     error_message=str(e),
        #     processing_time=processing_time
        # )
            return {"url":"unable to extract transcript from Document"}
        
        
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