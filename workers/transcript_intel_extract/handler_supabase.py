from typing import Optional
from supabase import create_client, Client
import os
from config_qa import SUPABASE_URL ,SUPABASE_SERVICE_KEY


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


def get_pdf_chunks_transcript(file_name):
    print("running supabase query...to get pdf chunks")
    rows =  supabase.table('pdf-transcripts').select('extracted_transcript').eq('file_name', f'{file_name}').execute()
    if not rows.data:
        print("no rows found")
        return False
    else:
        print("documents fetched")
        # print(rows.data)
        return rows.data[0]['extracted_transcript']
    
 
def get_pdf_transcript_and_meta(file_name):
    print("running supabase query to get transcript & meta...")
    rows =  supabase.table('pdf-transcripts').select('extracted_transcript,addn_meta').eq('file_name', f'{file_name}').execute()
    if not rows.data:
        print("no rows found")
        return False
    else:
        # print("documents supp")
        # print(rows.data)
        return rows.data[0]
    
def get_itdoc_mg_guidance(file_name,key='overview'):
    print("running supabase query...to get mg guidance")
    rows =  supabase.table('transcripts-intel').select('management_data').eq('file_name', f'{file_name}').execute()
    if not rows.data:
        print("no rows found")
        return False
    else:
        # print("documents supp",key)
        # print(rows.data)
        return rows.data[0]['management_data'][key] if rows.data[0]['management_data'] else False

def update_transcript_meta_entry(file_name, qa_start_key):
    try:
        # First, fetch the existing record to get current metadata
        existing_record = supabase.table('pdf-transcripts').select('addn_meta').eq('file_name', file_name).execute()
        
        if not existing_record.data:
            print(f"No record found for file: {file_name}")
            return None
        
        # Initialize empty dict if addn_meta is None
        current_addn_meta = existing_record.data[0].get('addn_meta') or {}
        print("current:", current_addn_meta)
        
        # Update the metadata with new qa_start_key while preserving existing entries
        current_addn_meta['qa_start_key'] = qa_start_key
        
        meta = {
            'addn_meta': current_addn_meta
        }
        
        # Update the record
        result = supabase.table('pdf-transcripts').update(meta).eq('file_name', file_name).execute()
        print("Updated document:", result)
        
        return result.data[0]['id'] if result.data else None
        
    except Exception as e:
        print(f"Error updating transcript meta: {str(e)}")
        return None

def insert_transcript_intel_entry(file_name,
                                  qa_data=None,
                                  mg_data=None,
                                  adn_meta=None 
                                    ):
    ts_document = {
        'qa_data': qa_data,
        'management_data': mg_data ,
        'file_name':file_name,
        'addn_meta': adn_meta,
    }

    result = supabase.table('transcripts-intel').insert(ts_document).execute()
    print("Inserted document:", )
    return result.data[0]['id'] if result.data else None  


def update_transcript_intel_entry(file_name,
                                  qa_data=None,
                                  mg_data=None,
                                  adn_meta=None ):
    meta = {
        'management_data':mg_data,
        'addn_meta':adn_meta
    }

    result = supabase.table('transcripts-intel').update(meta).eq('file_name', file_name).execute()
    print("Updated document:",file_name )
    return result.data[0]['id'] if result.data else None  

def fetch_management_data(file_name: str) -> dict:
    result = supabase.table('transcripts-intel').select('management_data').eq('file_name', file_name).execute()
    if not result.data:
        raise ValueError(f"No entry found for file_name: {file_name}")
    return result.data[0]['management_data'] or {}

def fetch_addn_metadata(file_name: str) -> dict:
    result = supabase.table('transcripts-intel').select('addn_meta').eq('file_name', file_name).execute()
    if not result.data:
        raise ValueError(f"No entry found for file_name: {file_name}")
    return result.data[0]['addn_meta'] or {}

def update_transcript_intel(file_name: str, meta: dict) -> str:
    result = supabase.table('transcripts-intel').update(meta).eq('file_name', file_name).execute()
    print("Updated document:", result)
    return result.data[0]['id'] if result.data else None