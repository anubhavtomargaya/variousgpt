from supabase import create_client, Client
import os
from config_qa import SUPABASE_URL ,SUPABASE_SERVICE_KEY


supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

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
    print("running supabase query...")
    rows =  supabase.table('pdf-transcripts').select('extracted_transcript').eq('file_name', f'{file_name}').execute()
    if not rows.data:
        print("no rows found")
        return False
    else:
        print("documents supp")
        print(rows.data)
        return rows.data[0]['extracted_transcript']
    
 
def get_pdf_transcript_and_meta(file_name):
    print("running supabase query...")
    rows =  supabase.table('pdf-transcripts').select('extracted_transcript,addn_meta').eq('file_name', f'{file_name}').execute()
    if not rows.data:
        print("no rows found")
        return False
    else:
        print("documents supp")
        # print(rows.data)
        return rows.data[0]
    
 
def update_transcript_meta_entry(file_name, qa_start_key):
    # First, fetch the existing record to get current metadata
    existing_record = supabase.table('pdf-transcripts').select('addn_meta').eq('file_name', file_name).execute()
    
    # Get existing additional metadata or initialize empty dict if none exists
    current_addn_meta = existing_record.data[0].get('addn_meta', {}) if existing_record.data else {}
    
    # Update the metadata with new qa_start_key while preserving existing entries
    current_addn_meta['qa_start_key'] = qa_start_key
    
    meta = {
        'addn_meta': current_addn_meta
    }

    result = supabase.table('pdf-transcripts').update(meta).eq('file_name', file_name).execute()
    print("Updated document:", result)
    return result.data[0]['id'] if result.data else None

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
        'management_data':mg_data
    }

    result = supabase.table('transcripts-intel').update(meta).eq('file_name', file_name).execute()
    print("Inserted document:", )
    return result.data[0]['id'] if result.data else None  

def fetch_management_data(file_name: str) -> dict:
    result = supabase.table('transcripts-intel').select('management_data').eq('file_name', file_name).execute()
    if not result.data:
        raise ValueError(f"No entry found for file_name: {file_name}")
    return result.data[0]['management_data'] or {}

def update_transcript_intel(file_name: str, meta: dict) -> str:
    result = supabase.table('transcripts-intel').update(meta).eq('file_name', file_name).execute()
    print("Updated document:", result)
    return result.data[0]['id'] if result.data else None