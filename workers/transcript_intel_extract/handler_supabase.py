from supabase import create_client, Client
import os
from config_qa import SUPABASE_URL ,SUPABASE_SERVICE_KEY


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
    
 
def get_pdf_transcript_and_meta(file_name):
    print("running supabase query...")
    rows =  supabase.table('pdf-transcripts').select('extracted_transcript,addn_meta').eq('file_name', f'{file_name}').execute()
    if not rows.data:
        print("no rows found")
        return False
    else:
        print("documents supp")
        print(rows.data)
        return rows.data[0]
    
 
def update_transcript_meta_entry(file_name, qa_start_key):
    meta = {
        'addn_meta': {'qa_start_key':qa_start_key}
    }

    result = supabase.table('pdf-transcripts').update(meta).eq('file_name', file_name).execute()
    print("Inserted document:", result)
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
    print("Inserted document:", result)
    return result.data[0]['id'] if result.data else None  


def update_transcript_intel_entry(file_name,
                                  qa_data=None,
                                  mg_data=None,
                                  adn_meta=None ):
    meta = {
        'management_data':mg_data
    }

    result = supabase.table('transcripts-intel').update(meta).eq('file_name', file_name).execute()
    print("Inserted document:", result)
    return result.data[0]['id'] if result.data else None  
