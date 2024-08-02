from supabase import create_client, Client
import os
from utils import SUPABASE_URL ,SUPABASE_SERVICE_KEY

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

def check_ts_exist(title):
    existing_ts = supabase.table('transcripts').select('*').eq('title', title).execute()
    print("exsiting doc",existing_ts)
    if not existing_ts.data:
        return False
    else:
        return existing_ts.data[0]
    
def insert_transcript_entry(text,title,chunks:dict,added_by=None):

    ts_document = {'text':text,
                     'title':title,
                     'chunks':chunks,
                     'added_by':added_by}
   
    supabase.table('transcripts').insert(ts_document).execute()
    return True 


def get_transcript_row(title)->dict:
    rows =  supabase.table('transcripts').select('*').eq('title', title).execute()
    if not rows.data:
        return False
    else:
        return rows.data[0]
    
def update_transcript_entry(title,ts_chunks):
    response = (supabase.table("transcripts")
                .update({"chunks": ts_chunks})
                .eq("title", title)
                .execute())
    return response

def handle_transcript_chunks_entry(title, chunk_transcript):
    #check if title exists already 
    row = check_ts_exist(title)
    if row:
        chunks = row['chunks']
    
    


if __name__ == '__main__':
    etitle = 'Frances_Election_Results_Explained'
    # print(get_transcript_row(etitle))
    print(check_ts_exist(etitle))