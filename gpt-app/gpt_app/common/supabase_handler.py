from supabase import create_client, Client
import os
from gpt_app.common.constants import SUPABASE_URL ,SUPABASE_SERVICE_KEY

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

def get_chunk_doc(filename)->dict:
    print("filname for em", filename)
    rows =  supabase.table('chunk_docs').select('*').eq('file_name', filename).execute()
    if not rows.data:
        return False
    else:
        return rows.data[0]['chunks']
        
def get_qa_records(filename,email)->dict:
    rows =  supabase.table('qa_records').select('*').eq('filename', filename).eq('email', email).execute()
    if not rows.data:
        return False
    else:
        return rows.data
    
def get_file_extn_doc(filename)->dict:
    rows =  supabase.table('chunk_docs').select('extn').eq('file_name', filename).execute()
    if not rows.data:
        return False
    else:
        return rows.data[0]
    
def get_list_docs():
    rows =  supabase.table('chunk_docs').select('file_name').neq('file_name', None).execute()
    if not rows.data:
        return False
    else:
        # print("sup")
        # print(rows.data)
        return [x['file_name']  for x  in rows.data ]
    
def get_list_pdf_transcripts():
    rows =  supabase.table('pdf-transcripts').select('company_name').execute()
    if not rows.data:
        return False
    else:
        print("sup")
        print(rows.data)
        return [x['company_name']for x in rows.data]
    
def get_list_pdf_transcripts():
    rows =  supabase.table('pdf-transcripts').select('file_name').neq('file_name',None).order('created_at', desc=True).execute()
    if not rows.data:
        return False
    else:
        print("sup")
        print(rows.data)
        print(rows.data[0]['file_name'])
        return [x['file_name']  for x in rows.data]
    
def get_company_transcript_data():
    rows = supabase.table('pdf-transcripts').select('company_name,quarter,financial_year,file_name').neq('file_name', None).order('created_at', desc=True).execute()
    if not rows.data:
        return False
    else:
        # Group the data by company
        grouped_data = {}
        for row in rows.data:
            company = row['company_name']
            if company not in grouped_data:
                grouped_data[company] = []
            grouped_data[company].append({
                'quarter': row['quarter'],
                'financial_year': row['financial_year'],
                'file_name': row['file_name']
            })
        
        return grouped_data
    
def get_pdf_chunks_transcript(file_name):
    print("running supabase query...")
    rows =  supabase.table('pdf-transcripts').select('company_name,quarter,financial_year,extracted_transcript').eq('file_name', f'{file_name}').execute()
    if not rows.data:
        print("no rows found")
        return False
    else:
        print("documents supp")
        print(rows.data)
        return rows.data[0]
    
def get_file_meta(file_name):
    print("running supabase query...")
    rows =  supabase.table('pdf-transcripts').select('company_name,quarter,financial_year').eq('file_name', f'{file_name}').execute()
    if not rows.data:
        print("no rows found")
        return False
    else:
        print("documents supp")
        print(rows.data)
        return rows.data[0]
    
def get_itdoc_qa_secrion(file_name):
    print("running supabase query...")
    rows =  supabase.table('transcripts-intel').select('qa_data').eq('file_name', f'{file_name}').execute()
    if not rows.data:
        print("no rows found")
        return False
    else:
        print("documents supp")
        print(rows.data)
        return rows.data[0]['qa_data']['section_qa']
    
def get_itdoc_mg_guidance(file_name):
    print("running supabase query...")
    rows =  supabase.table('transcripts-intel').select('management_data').eq('file_name', f'{file_name}').execute()
    if not rows.data:
        print("no rows found")
        return False
    else:
        print("documents supp")
        print(rows.data)
        return rows.data[0]['management_data']['overview']
    
    
    
def get_company_content_all(copname):
    print("running supabase query...")
    rows =  supabase.table('company-content').select('company_name,upcoming,latest,faq').eq('company_name', f'{copname}').execute()
    if not rows.data:
        print("no rows found")
        return False
    else:
        print("documents supp")
        print(rows.data)
        return rows.data
    
    
def get_content_top_questions(file_name):
    print("running supabase query...")
    rows =  supabase.table('content-docs').select('top_qa').eq('file_name', f'{file_name}').execute()
    if not rows.data:
        print("no rows found")
        return False
    else:
        print("documents supp")
        # print(rows.data)
        return rows.data[0]['top_qa']
    
def get_list_transcripts():
    rows =  supabase.table('transcripts').select('title').execute()
    if not rows.data:
        return False
    else:
        print("sup")
        print(rows.data)
        return [x['title']for x in rows.data]

def check_user_exist(email):
    existing_user = supabase.table('users').select('*').eq('email', email).execute()
    print(existing_user)
    if not existing_user.data:
        return False
    else:
        return existing_user.data 
    
def check_yt_exist(link):
    existing_video = supabase.table('imports_youtube').select('*').eq('link', link).execute()
    print("exsiting vdo",existing_video)
    if not existing_video.data:
        return False
    else:
        return existing_video.data 
    
def check_ts_exist(title):
    existing_ts = supabase.table('transcripts').select('*').eq('title', title).execute()
    print("exsiting doc",existing_ts)
    if not existing_ts.data:
        return False
    else:
        return existing_ts.data 
    
def check_tdoc_exist(filename):
    existing_tdoc = supabase.table('chunk_docs').select('*').eq('file_name', filename).execute()
    # print("exsiting vdo",existing_tdoc)
    if not existing_tdoc.data:
        return False
    else:
        return existing_tdoc.data 
    
def insert_yt_entry(link,meta,added_by):

    user_document = {
            
        
            'link': link,
            'added_by': added_by,
            'meta': meta
        }

        # Insert user into the users table
    supabase.table('imports_youtube').insert(user_document).execute()
    return True 

def insert_classifier_entry(import_filename,given_filename,file_metadata={}):

    classifier_doc = {
            
        
            'import_filename': import_filename,
            'given_file_name': given_filename,
            'file_metadata': file_metadata,
            'classifier_version':'v0'
        }

        # Insert user into the users table
    supabase.table('pdf-classification').insert(classifier_doc).execute()
    return True 

def insert_ts_entry(title,text,added_by):

    user_document = {
            
        
            'title': title,
            'added_by': added_by,
            'text': text
        }

        # Insert user into the users table
    supabase.table('transcripts').insert(user_document).execute()
    return True 
from gpt_app.common.record_handler import QARecord
def insert_qa_entry(qa_document
                    ):


        # Insert user into the users table
    supabase.table('qa_records').insert(qa_document).execute()
    return True 

def insert_chunk_doc_entry(doc:dict,added_by):

    user_document = doc
    user_document['metadata']['added_by'] =added_by
    supabase.table('chunk_docs').insert(user_document).execute()
    return True 


def update_doc_chunk(file,rich_chunks):
    response = (supabase.table("chunk_docs")
                .update({"chunks": rich_chunks})
                .eq("file_name", file)
                .execute())
    return response

def insert_yt_entry(link,meta,added_by):

    user_document = {
            
        
            'link': link,
            'added_by': added_by,
            'meta': meta
        }

        # Insert user into the users table
    supabase.table('imports_youtube').insert(user_document).execute()
    return True 


def save_user(email, name, google_id):
    # existing =  check_user_exist(email)
    # if not existing:
        # Create a new user document
        user_document = {
           
            'email': email,
            'name': name,
            'google_id': google_id
        }

        # Insert user into the users table
        supabase.table('users').insert(user_document).execute()
        return True 
    # else:
        # return existing

# print(save_user(email='test@test.com',name='test_user',google_id='100001000'))

## PDF WORKER


def check_pdf_exist(company_name, quarter, financial_year, doc_type):
    existing_ts = supabase.table('pdf-transcripts') \
                          .select('*') \
                          .eq('company_name', company_name) \
                          .eq('quarter', quarter) \
                          .eq('financial_year', financial_year) \
                          .eq('doc_type', doc_type) \
                          .execute()
    print("existing doc", existing_ts)
    if not existing_ts.data:
        return False
    else:
        return existing_ts.data[0]
    
def check_transcript_extracted(transcript_id):
    existing_ts = supabase.table('pdf-transcripts') \
                          .select('extracted_transcript') \
                          .eq('id', transcript_id) \
                          .execute()
    print("existing extracted_transcript field:", existing_ts)
    if existing_ts.data and existing_ts.data[0]['extracted_transcript'] is not None:
        return True
    else:
        print("transcript doesnt exist")
        return False
    
def insert_initial_transcript_entry(company_name,
                                    quarter, 
                                    financial_year,
                                    doc_type,
                                    description,
                                    key_people
                                    ):
    ts_document = {
        'company_name': company_name,
        'quarter': quarter,
        'financial_year': financial_year,
        'doc_type': doc_type,
        'description': description,
        'key_people': key_people,
    }

    result = supabase.table('pdf-transcripts').insert(ts_document).execute()
    print("Inserted document:", result)
    return result.data[0]['id'] if result.data else None  


def get_transcript_row(id)->dict:
    rows =  supabase.table('pdf-transcripts').select('*').eq('id', id).execute()
    if not rows.data:
        print("No rows found for the id")
        return False
    else:
        print("rows:",rows.data)
        return rows.data[0]
    



def update_transcript_pdf_entry(transcript_id, extracted_transcript, extra_text):
    update_document = {
        'extracted_transcript': extracted_transcript,
        'extra_text': extra_text
    }

    result = supabase.table('pdf-transcripts').update(update_document).eq('id', transcript_id).execute()
    print("Updated document:")
    return result

if __name__=='__main__':
    f = 'fy25_q1_earnings_call_transcript_zomato_limited_zomato.pdf'
    f = 'fy-2025_q1_earnings_call_transcript_amara_raja_energy_&_mobility_limited_are&m.pdf'

    def test_get_qa_section():
        return get_itdoc_qa_secrion(f)
    def test_get_content_top_qa():
        return get_content_top_questions(f)
    
    # print(test_get_qa_section())
    print(test_get_content_top_qa())
