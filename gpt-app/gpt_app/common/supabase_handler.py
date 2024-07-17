from supabase import create_client, Client
import os
from gpt_app.common.constants import SUPABASE_URL ,SUPABASE_SERVICE_KEY

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

def get_chunk_doc(filename)->dict:
    rows =  supabase.table('chunk_docs').select('*').eq('file_name', filename).execute()
    if not rows.data:
        return False
    else:
        return rows.data[0]['chunks']
    
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
    print("exsiting vdo",existing_ts)
    if not existing_ts.data:
        return False
    else:
        return existing_ts.data 
    
def insert_yt_entry(link,meta,added_by):

    user_document = {
            
        
            'link': link,
            'added_by': added_by,
            'meta': meta
        }

        # Insert user into the users table
    supabase.table('imports_youtube').insert(user_document).execute()
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