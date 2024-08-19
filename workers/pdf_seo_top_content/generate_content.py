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


def service_extract_seo_top_questions(file_name,added_by=None):
    txt = get_pdf_txt(file_name)
    print("gen seo doc for file:",file_name)

    chunks = split_document(txt,CHUNK_PARAMS[0],CHUNK_PARAMS[1])
    big_chunk  = chunks[0] # only take first chunk
    
    try:

        questions = generate_seo.top_questions(big_chunk,
                                            num_questions=6)
        
        # seo_content = generate_seo.generate_answers(big_chunk,
                                                    # questions)
        
    except Exception as e:
        raise Exception("Error in generate.seo : %s",e)
    try:
        doc = create_seo_content_doc_for_file(filename=file_name,
                                              top_questions=questions,
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
    
# ----------------- # 

    def test_service_seo_content():
        return service_extract_seo_top_questions(f)

# ----------------- # 


    # print(test_get_text_chunk())
    # print(test_generate_questions())
    # print(test_generate_seo_qa())
    print(test_service_seo_content())

    