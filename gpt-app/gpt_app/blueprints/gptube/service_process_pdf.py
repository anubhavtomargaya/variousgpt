

from gpt_app.common.utils_dir import _make_file_path
from  gpt_app.blueprints.gptube.load_pdf import download_pdf_from_bucket
from  gpt_app.blueprints.gptube.helpers_pdf import extract_text_from_pdf_bytes
from gpt_app.common.utils_text import split_document, count_words,generate_hash_key
from gpt_app.common.supabase_handler import insert_chunk_doc_entry

CHUNK_PARAMS  = (2000,100)

def create_doc_for_file(filename, chunks:list, meta:dict={}):
    """ make the dict in first stage of storing doc (towards common format)
    """
    meta['chunks_num']= len(chunks)
    c = {n:{
        'chunk_text':v,
        'chunk_embedding':None,
        'chunk_meta':{ }} for n,v in enumerate(chunks)}

    doc = {'file_name':filename,
           'chunks':c,
           'metadata':meta
           }
   
    return doc

def process_pdf_to_doc(file):
    bdata = download_pdf_from_bucket(file)
    txt = extract_text_from_pdf_bytes(bdata)
    meta = {'chunk_params':CHUNK_PARAMS}
    chunks = split_document(txt,CHUNK_PARAMS[0],CHUNK_PARAMS[1])
    doc = create_doc_for_file(chunks=chunks,
                             filename=file,
                             meta=meta)
    sp = insert_chunk_doc_entry(doc=doc,added_by='test')
    print(sp)

    return True 
   


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