from typing import Optional
from supabase import create_client, Client
import os
from utils_em import SUPABASE_URL ,SUPABASE_SERVICE_KEY

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

def get_chunk_doc(filename)->dict:
    rows =  supabase.table('chunk_docs').select('*').eq('file_name', filename).execute()
    if not rows.data:
        return False
    else:
        return rows.data[0]['chunks']

def check_tdoc_exist(filename):
    existing_tdoc = supabase.table('chunk_docs').select('*').eq('file_name', filename).execute()
    # print("exsiting vdo",existing_tdoc)
    if not existing_tdoc.data:
        return False
    else:
        return existing_tdoc.data 

def insert_content_doc_entry(doc:dict,added_by):
    print("inserting...")
    user_document = doc
    user_document['metadata']['added_by'] =added_by
    supabase.table('content-docs').insert(user_document).execute()
    return True 

def upsert_content_doc_entry(doc: dict, added_by: str) -> bool:
    print("upserting...")
    user_document = doc
    user_document['metadata']['added_by'] = added_by
    
    # Perform upsert operation using file_name as the unique key
    supabase.table('content-docs')\
        .upsert(user_document, on_conflict='file_name')\
        .execute()
    
    return True

def update_doc_chunk(file,rich_chunks):
    response = (supabase.table("chunk_docs")
                .update({"chunks": rich_chunks})
                .eq("file_name", file)
                .execute())
    return response


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
    

if __name__ == '__main__':
    etitle = 'Frances_Election_Results_Explained'
    # print(get_transcript_row(etitle))
    