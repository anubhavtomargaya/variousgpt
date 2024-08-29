from supabase import create_client, Client
import os
from utils_em import SUPABASE_URL ,SUPABASE_SERVICE_KEY

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)


def insert_chunk_doc_entry(doc:dict,added_by):
    print("inserting...")
    user_document = doc
    user_document['metadata']['added_by'] =added_by
    supabase.table('chunk_docs').insert(user_document).execute()
    return True 
