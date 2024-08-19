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

def update_doc_chunk(file,rich_chunks):
    response = (supabase.table("chunk_docs")
                .update({"chunks": rich_chunks})
                .eq("file_name", file)
                .execute())
    return response


if __name__ == '__main__':
    etitle = 'Frances_Election_Results_Explained'
    # print(get_transcript_row(etitle))
    