

from gpt_app.common.utils_dir import _make_file_path
from  gpt_app.blueprints.gptube.load_pdf import download_pdf_from_bucket
from  gpt_app.blueprints.gptube.helpers_pdf import extract_text_from_pdf_bytes
from gpt_app.common.utils_text import split_document, count_words,generate_hash_key

def insert_chunk_doc(doc):
    """ insert the file dict in first stage of storing doc (towards common format)
    """
    pass 

def process(file):
    bdata = download_pdf_from_bucket(file)
    txt = extract_text_from_pdf_bytes(bdata)
    chunks = split_document(txt,2000,100)
    c = {n:{
        'hash':generate_hash_key(v),
        'chunk_text':v,
            'chunk_embedding':None,
            'chunk_meta':{ }} for n,v in enumerate(chunks)}
    # print(c)
    doc = {'filename':file,
           'chunks':c,
           'meta':{'chunks_num':len(chunks)}
           }
    print(doc)

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
    
    def test_process():
        return process(f)
    
    # print(test_download())
    # print(test_mupdf_text())
    # print(test_split_text())
    print(test_process())