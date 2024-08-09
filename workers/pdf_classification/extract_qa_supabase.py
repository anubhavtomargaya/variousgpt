from supabase import create_client, Client
import os
from extract_qa_config import SUPABASE_URL ,SUPABASE_SERVICE_KEY


supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

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
    
 
def update_transcript_meta_entry(file_name, qa_start_key):
    meta = {
        'addn_meta': {'qa_start_key':qa_start_key}
    }

    result = supabase.table('pdf-transcripts').update(meta).eq('file_name', file_name).execute()
    print("Inserted document:", result)
    return result.data[0]['id'] if result.data else None  