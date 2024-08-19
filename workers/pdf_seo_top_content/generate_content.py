#utils 
from load_pdf import download_pdf_from_bucket
import fitz
from utils_em import split_document, create_seo_content_doc_for_file
from db_supabase import insert_content_doc_entry
import generate_seo
APP_BUCKET = 'gpt-app-data'
PROC_PDF_BUCKET = 'pdf-transcripts'
CHUNK_PARAMS  = (13000,100)

def extract_text_from_pdf_bytes(pdf_bytes):
    """Extracts text from a PDF file in memory."""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    text = ""
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text += page.get_text()
    return text.replace('\n',' ')

def get_pdf_txt(file):
    bdata = download_pdf_from_bucket(file,bucket=PROC_PDF_BUCKET)
    txt = extract_text_from_pdf_bytes(bdata)
    print('text')
    # print(txt)
    return txt 


CHUNKS_TO_PROC = 1
def service_process_to_chunk_doc(file_name,added_by=None):
    txt = get_pdf_txt(file_name)
    print("file",file_name)
    meta = {'chunk_params':CHUNK_PARAMS}
    chunks = split_document(txt,CHUNK_PARAMS[0],CHUNK_PARAMS[1])
    top_questions = [ ]
    for chunk in chunks:
        questions = generate_seo.top_questions()
    try:
        doc = create_seo_content_doc_for_file(filename=file_name,
                                              )
        sp = insert_content_doc_entry(doc=doc,added_by=added_by)
        print(sp)
        return True
    except Exception as e:
        print("dbError: alreayd exists?",e)
        raise e



if __name__=='__main__':
    f = 'fy-2025_q1_earnings_call_transcript_amara_raja_energy_&_mobility_limited_are&m.pdf'

    def test_get_text_chunk():
        txt= get_pdf_txt(f)
        return split_document(txt)
    
    def test_generate_questions():
        txt = get_pdf_txt(f)
        big_chunk = split_document(txt,CHUNK_PARAMS[0])[0]
        questions = generate_seo.top_questions(big_chunk)
        return questions
    
    def test_generate_seo_qa():
        txt = get_pdf_txt(f)
        big_chunk = split_document(txt,CHUNK_PARAMS[0])[0]
        questions = generate_seo.top_questions(big_chunk)
        seo_content = generate_seo.generate_answers(big_chunk,questions)
        return seo_content
    
    # print(test_get_text_chunk())
    # print(test_generate_questions())
    print(test_generate_seo_qa())

    