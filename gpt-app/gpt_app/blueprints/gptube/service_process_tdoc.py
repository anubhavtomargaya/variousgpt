from gpt_app.common.dirs import TS_DIR
from  gpt_app.common.utils_dir import download_blob_to_memory, _make_file_path, check_blob, check_ts_dir, save_transcript_text_json, upload_blob_to_gcs_bucket_by_filename
from  gpt_app.common.utils_dir import client as gcs_client
from  gpt_app.blueprints.gptube.helpers_db import create_doc_for_file
from gpt_app.common.utils_text import split_document, count_words,generate_hash_key
from gpt_app.common.supabase_handler import check_tdoc_exist, insert_chunk_doc_entry

CHUNK_PARAMS_TDOC = (1000,100)

def process_transcripton_doc_to_rag(file_name):
    if check_tdoc_exist(file_name):
        return False #use this func when the process is called
    sth = download_blob_to_memory(gcs_client,file_name,TS_DIR)
    if not sth or not isinstance(sth,dict):
        raise Exception("file not present in bucket")
    text = sth.get('text',None)
    if not text:
        raise Exception("unable to find 'text' in the transcript doc tdoc")
    meta = {'chunk_params':CHUNK_PARAMS_TDOC}
    chunks = split_document(text,CHUNK_PARAMS_TDOC[0],CHUNK_PARAMS_TDOC[1])
    doc = create_doc_for_file(chunks=chunks,
                             filename=file_name,
                             meta=meta)
    
    sp = insert_chunk_doc_entry(doc=doc,added_by='test')
    print(sp)

    return True 



if __name__ == '__main__':
    f = 'Hindustan_Aeronautics_Ltd_Q4_FY2023-24_Earnings_Conference_Call.json'

    # def test_downloading_tdoc_from_gcs():
    #     return download_blob_to_tmpfile(gcs_client,f,TS_DIR)
    

    def test_reading_memory_tdoc_from_gcs():
        return download_blob_to_memory(gcs_client,f,TS_DIR)
    
    def test_process_tdoc():
        return process_transcripton_doc_to_rag(f)
    
    # print(test_downloading_tdoc_from_gcs())
    print(test_process_tdoc())
    # print(test_reading_memory_tdoc_from_gcs())