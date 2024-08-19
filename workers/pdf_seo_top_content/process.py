from load_pdf import download_pdf_from_bucket, download_pdf_from_pdf_bucket_file, load_pdf_into_bucket
from db_supabase import check_tdoc_exist, get_chunk_doc,insert_chunk_doc_entry, update_doc_chunk
from utils_em import *
import fitz 

APP_BUCKET = 'gpt-app-data'
PROC_PDF_BUCKET = 'pdf-transcripts'
CHUNK_PARAMS  = (2000,100)

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

openai_client = get_openai_client()

# def get_stranger_file_classification_name(file,added_by=None):
#     path = download_pdf_from_pdf_bucket_file(file_name=file,
#                                              bucket=APP_BUCKET)
#     classificaiton = classify_pdf_transcript(path)
#     if classificaiton:
#         print("earning call detected! path:", classificaiton) 
#         # return classificaiton
#         url = load_pdf_into_bucket(path,destination_filename=classificaiton,bucket=PROC_PDF_BUCKET)
#         print("file uploaded ,url:",url)
#         return url 
#     else:
#         print("earning call NOT detected! response", classificaiton) 
#         return False 

def service_embed_pdf_chunks(file):
    chunks_dict = get_chunk_doc(file)
    if not chunks_dict:
        raise Exception("No chunks dict there for embedding")
    for k,v in chunks_dict.items():
        chnk = v['chunk_text']
        if not chunks_dict[k]['chunk_embedding']:
            chunks_dict[k]['chunk_embedding'] = get_embedding(client=openai_client,
                                                          text=chnk)
            ures = update_doc_chunk(file=file,rich_chunks=chunks_dict)
            print(ures)
        else:
            pass
    return True
def service_process_to_chunk_doc(file_name,added_by=None):
    txt = get_pdf_txt(file_name)
    print("file",file_name)
    meta = {'chunk_params':CHUNK_PARAMS}
    chunks = split_document(txt,CHUNK_PARAMS[0],CHUNK_PARAMS[1])
    doc = create_doc_for_file(chunks=chunks,
                            filename=file_name,
                            e='pdf',
                            meta=meta)
    try:

        sp = insert_chunk_doc_entry(doc=doc,added_by=added_by)
        print(sp)
        return True
    except Exception as e:
        print("dbError: alreayd exists?",e)
        raise e
    
def service_process_pdf_to_rag(given_file_name,added_by=None):
    tdoc = check_tdoc_exist(given_file_name)
    if  tdoc:
        return False
    else:        
        try:
            chunk_doc = service_process_to_chunk_doc(file_name=given_file_name)
            if chunk_doc:
                print("chunking success")
            else:
                print("chunking failed")
                
                return False
        except Exception as e:
            print("Chunking error..",e)
            return {"filename":given_file_name,"success":False}
        try:
            embedding_ = service_embed_pdf_chunks(given_file_name)
            if embedding_:
                return True,given_file_name
            else:
                return False,given_file_name
        except Exception as e:
            print("Embedding error..",e)
            return {"filename":given_file_name,"success":False}
   
if __name__=='__main__':
    file_name = 'Raymond_Conference_Call_TranscripQ4-fy24.pdf'
    def test_check_tdoc():
        return check_tdoc_exist(file_name)
    
    def test_get_pdf_text():
        return get_pdf_txt(file_name)
    
    def test_full_process():
        return service_process_pdf_to_rag(file_name)
    # print(test_check_tdoc())
    # print(test_get_pdf_text())
    print(test_full_process())

        