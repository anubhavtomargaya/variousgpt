

from gpt_app.common.utils_dir import _make_file_path
from  gpt_app.blueprints.gptube.load_pdf import download_pdf_from_bucket, download_pdf_from_pdf_bucket_file, download_transcript_json_from_bucket
from  gpt_app.blueprints.gptube.helpers_pdf import extract_text_from_pdf_bytes
from  gpt_app.blueprints.gptube.helpers_db import create_doc_for_file
from gpt_app.common.utils_text import split_document, count_words,generate_hash_key
from gpt_app.common.supabase_handler import check_tdoc_exist, insert_chunk_doc_entry
from gpt_app.blueprints.gptube.process_pdf_text import service_extract_transcript_texts

CHUNK_PARAMS  = (2000,100)



def get_pdf_txt(file):
    bdata = download_pdf_from_bucket(file)
    txt = extract_text_from_pdf_bytes(bdata)
    print('text')
    print(txt)
    return txt 
import json
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

def process_pdf_to_doc(file,added_by=None):
    tdoc = check_tdoc_exist(file)
    if  tdoc:
        return False
    else:
            
        txt = get_pdf_txt(file)
        print("file",file)
        meta = {'chunk_params':CHUNK_PARAMS}
        chunks = split_document(txt,CHUNK_PARAMS[0],CHUNK_PARAMS[1])
        doc = create_doc_for_file(chunks=chunks,
                                filename=file,
                                e='pdf',
                                meta=meta)
        sp = insert_chunk_doc_entry(doc=doc,added_by=added_by)
        print(sp)

        return True 
   

def process_pdf_to_doc_v2(file,row,added_by=None):
    path = download_pdf_from_pdf_bucket_file(file)
    print("row",row)
    print("path",path)
    result = service_extract_transcript_texts(path,row)

    return result
   


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