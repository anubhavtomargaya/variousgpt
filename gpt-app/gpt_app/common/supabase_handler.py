from typing import Optional
from supabase import create_client, Client
import os
from gpt_app.common.constants import SUPABASE_URL ,SUPABASE_SERVICE_KEY

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

def supabase_insert(table_name: str, data: dict) -> Optional[dict]:
    """
    Generic function to insert data into Supabase table and handle response
    
    Args:
        table_name (str): Name of the Supabase table
        data (dict): Data to insert
        
    Returns:
        Optional[dict]: First record of inserted data if successful, None otherwise
    """
    try:
        result = supabase.table(table_name).insert(data).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Supabase insert error for table {table_name}: {str(e)}")
        return None
    
def get_search_suggestions(query: str, limit: int = 5) -> list:
    """
    Get search suggestions using Supabase
    """
    try:
        # Clean the query
        query = query.strip()
        if len(query) < 2:
            return []
            
        # Query Supabase using ilike for case-insensitive search
        result = supabase.table('pdf-transcripts')\
            .select('company_name, ticker')\
            .or_(f"company_name.ilike.%{query}%,ticker.ilike.%{query}%")\
            .limit(limit)\
            .execute()
            
        # Convert to list of unique companies
        seen = set()
        suggestions = []
        
        if result.data:
            for item in result.data:
                key = (item['company_name'], item['ticker'])
                if key not in seen and len(suggestions) < limit:
                    seen.add(key)
                    suggestions.append({
                        'company_name': item['company_name'],
                        'ticker': item['ticker']
                    })
                    
        return suggestions
        
    except Exception as e:
        print(f"Error in search suggestions: {str(e)}")
        return []
    
def get_latest_transcripts(limit: int = 5, offset: int = 0):
    """
    Queries the pdf-transcripts table and returns the latest transcripts with specified columns.
    Orders results by created_at timestamp in descending order.
    
    Args:
        limit (int, optional): Maximum number of records to return. Defaults to 5.
        offset (int, optional): Number of records to skip. Defaults to 0.
    
    Returns:
        list: A list of dictionaries containing transcript details
              Each dictionary has keys: filename, quarter, financial_year, company_name, ticker
    """
    try:
        # Query the table with pagination
        result = supabase.table('pdf-transcripts')\
            .select('file_name,date,quarter,financial_year,company_name,ticker,created_at')\
            .order('created_at', desc=True)\
            .limit(limit)\
            .offset(offset)\
            .execute()
        
        # Transform the results into the desired format
        transcripts = []
        if result.data:
            for record in result.data:
                transcript = {
                    'file_name': record['file_name'],
                    'quarter': record['quarter'],
                    'date': record['date'],
                    'financial_year': record['financial_year'],
                    'company_name': record['company_name'],
                    'ticker': record['ticker']
                }
                transcripts.append(transcript)
                
        return transcripts
        
    except Exception as e:
        print(f"Error fetching latest transcripts: {str(e)}")
        return []

def get_pipeline_events(process_id: str):
    """Query pipeline events for a specific process"""
    try:
        result = supabase.table('pipeline_events')\
            .select('*')\
            .eq('process_id', process_id)\
            .order('created_at', desc=False)\
            .execute()
        print("pip evs",result.data)
        return result.data if result.data else None
    except Exception as e:
        print(f"Error querying pipeline events: {str(e)}")
        return None

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
        # print(rows.data)
        return rows.data[0]
    
def get_prompts_by_name(prompt_name, prompt_version):
    print("running supabase query...to get prompt data")
    filters = {'name': prompt_name}
    if prompt_version:
        filters['version'] = prompt_version
            
    result = supabase.table('prompts').select("*").match(filters).execute()
        # result = self.supabase.table('prompts').select("*").eq('name', name).execute()

    if not result.data:
        print("no rows found")
        return False
    else:
        print("documents supp")
        # print(result.data)
        return result.data[0] 
        return rows.data[0]
    
def get_file_meta(file_name):
    print("running supabase query...")
    print('filename',file_name)
    rows =  supabase.table('pdf-transcripts').select('company_name,date,ticker,quarter,date,financial_year,addn_meta').eq('file_name', f'{file_name}').execute()
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
def get_itdoc_mg_tags(file_name):
    print("running supabase query...")
    rows =  supabase.table('transcripts-intel').select('management_data').eq('file_name', f'{file_name}').execute()
    if not rows.data:
        print("no rows found")
        return False
    else:
        print("documents supp")
        print(rows.data)
        return rows.data[0]['management_data'].get('tags',None) if rows.data[0]['management_data'] else False
    
def get_itdoc_mg_guidance(file_name,key='overview'):
    print("running supabase query...")
    rows =  supabase.table('transcripts-intel').select('management_data').eq('file_name', f'{file_name}').execute()
    if not rows.data:
        print("no rows found")
        return False
    else:
        print("documents supp",key)
        # print(rows.data)
        return rows.data[0]['management_data'][key] if rows.data[0]['management_data'] else False

def get_files_without_tags():
    print("Querying for files without management tags...")
    query = supabase.table('transcripts-intel') \
        .select('file_name, management_data') \
        .is_('management_data->>tags', 'null') \
        .execute()
    
    if not query.data:
        print("No files found without tags")
        return []
    
    files = [row['file_name'] for row in query.data]
    print(f"Found {len(files)} files without tags")
    return files

def get_itdoc_structured_summary(file_name):
    """
    Fetch structured summary data from the database
    """
    print("Fetching structured summary from database...")
    try:
        rows = supabase.table('transcripts-intel').select('management_data').eq('file_name', f'{file_name}').execute()
        if not rows.data:
            print("No structured summary found")
            return False
        
        management_data = rows.data[0].get('management_data', {})
        if not management_data:
            return False
            
        return management_data.get('struct_summary', False)
    except Exception as e:
        print(f"Error fetching structured summary: {str(e)}")
        return False
    
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
    
def get_company_list():
    print("running supabase query...")
    rows =  supabase.table('company-data').select('company_name,tags').eq('disable',False).execute()
    if not rows.data:
        print("no rows found")
        return False
    else:
        print("documents supp")
        # print(rows.data)
        return rows.data
    
    
def get_company_file_names(company_name):
    print("running supabase query...")
    print(company_name)
    rows =  supabase.table('pdf-transcripts').select('file_name').eq('company_name', f'{company_name}').execute()
    if not rows.data:
        print("no rows found")
        return False
    else:
        print("documents supp")
        print(rows.data)
        return [x['file_name'] for x in rows.data]
        return rows.data[0]['top_qa']


def get_distinct_transcript_files():
    """
    Queries the pdf-transcripts table and returns a list of all distinct file names.
    
    Returns:
        list: A list of unique file names from the pdf-transcripts table
    """
    # Query the table selecting only distinct file names
    result = supabase.table('pdf-transcripts').select('file_name').execute()
    
    # Extract file names from the result and return as a list
    file_names = [record['file_name'] for record in result.data] if result.data else []
    
    # Remove any duplicates (though they shouldn't exist due to table structure)
    unique_files = list(set(file_names))
    
    return sorted(unique_files)  # Return sorted list for consistency
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
    f = 'fy-2024_q1_earnings_call_transcript_neuland_laboratories_524558.pdf'
    # f = 'fy2024_q2_gravita_india_limited_quarterly_earnings_call_transcript_gravita.pdf'
    def test_get_qa_section():
        return get_itdoc_qa_secrion(f)
    def test_get_struct_summary():
        return get_itdoc_structured_summary(f)
    def test_get_content_top_qa():
        return get_content_top_questions(f)
    
    def test_get_intel_files():
        return get_files_without_tags()
    
    def test_get_latest_files():
        return get_latest_transcripts()
    
    def test_get_prompt_names():
        return get_prompts_by_name(prompt_name='earnings_call_takeaway',prompt_version=1)
    

    
    # print(test_get_qa_section())
    # print(test_get_content_top_qa())
    # print(test_get_struct_summary())
    print(test_get_prompt_names())
    # print(test_get_intel_files())
    # print(test_get_latest_files())
