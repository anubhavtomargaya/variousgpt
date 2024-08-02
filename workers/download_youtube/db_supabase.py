import json
from pathlib import Path
from supabase import create_client, Client
import os
# from utils import SUPABASE_URL ,SUPABASE_SERVICE_KEY
## setup.nb
CONFIG_FILE='env.json'
def _load_config():
    with open(Path(Path(__file__).parent.resolve(),CONFIG_FILE)) as f:
        return json.load(f)
    
configs = _load_config()
SUPABASE_URL =configs['SUPABASE_URL']
SUPABASE_SERVICE_KEY = configs['SUPABASE_SERVICE_KEY']

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)


def check_yt_exist(link):
    existing_video = supabase.table('imports_youtube').select('*').eq('link', link).execute()
    print("exsiting vdo",existing_video)
    if not existing_video.data:
        return False
    else:
        return existing_video.data 
    
    
def insert_yt_entry(link,meta,added_by):

    user_document = {
            
        
            'link': link,
            'added_by': added_by,
            'meta': meta
        }

        # Insert user into the users table
    supabase.table('imports_youtube').insert(user_document).execute()
    print("entry inserted in database ")
    return True 

# def get_transcript_row(title)->dict:
#     rows =  supabase.table('transcripts').select('*').eq('title', title).execute()
#     if not rows.data:
#         return False
#     else:
#         return rows.data[0]
    
# def update_transcript_entry(title,ts_chunks):
#     response = (supabase.table("transcripts")
#                 .update({"chunks": ts_chunks})
#                 .eq("title", title)
#                 .execute())
#     return response

# def handle_transcript_chunks_entry(title, chunk_transcript):
#     #check if title exists already 
#     row = check_ts_exist(title)
#     if row:
#         chunks = row['chunks']
    
    


if __name__ == '__main__':
    etitle = 'Frances_Election_Results_Explained'
    # print(get_transcript_row(etitle))
    # print(check_yt_exist(etitle))