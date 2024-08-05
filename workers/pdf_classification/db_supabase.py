from supabase import create_client, Client
import os
from utils_ts import SUPABASE_URL ,SUPABASE_SERVICE_KEY

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

def insert_classifier_entry(import_filename,given_filename,file_metadata={}):

    classifier_doc = {
            
        
            'import_filename': import_filename,
            'given_file_name': given_filename,
            'file_metadata': file_metadata,
            'classifier_version':'v0',
            'user_id':'catwoman'
        }

        # Insert user into the users table
    supabase.table('pdf-classification').insert(classifier_doc).execute()
    return True 
def check_pdf_exist(company_name, quarter, financial_year, doc_type):
    existing_ts = supabase.table('pdf-transcripts') \
                          .select('*') \
                          .eq('company_name', company_name) \
                          .eq('quarter', quarter) \
                          .eq('financial_year', financial_year) \
                          .eq('doc_type', doc_type) \
                          .execute()
    print("existing doc", existing_ts)
    if not existing_ts.data:
        return False
    else:
        return existing_ts.data[0]
    
def check_transcript_extracted(transcript_id):
    existing_ts = supabase.table('pdf-transcripts') \
                          .select('extracted_transcript') \
                          .eq('id', transcript_id) \
                          .execute()
    print("existing extracted_transcript field:", existing_ts)
    if existing_ts.data and existing_ts.data[0]['extracted_transcript'] is not None:
        return True
    else:
        print("transcript doesnt exist")
        return False
    
def insert_initial_transcript_entry(company_name,
                                    quarter, 
                                    file_name,
                                    financial_year,
                                    doc_type,
                                    description,
                                    key_people
                                    ):
    ts_document = {
        'company_name': company_name,
        'quarter': quarter,
        'file_name':file_name,
        'financial_year': financial_year,
        'doc_type': doc_type,
        'description': description,
        'key_people': key_people,
    }

    result = supabase.table('pdf-transcripts').insert(ts_document).execute()
    print("Inserted document:", result)
    return result.data[0]['id'] if result.data else None  


def get_transcript_row(id)->dict:
    rows =  supabase.table('pdf-transcripts').select('*').eq('id', id).execute()
    if not rows.data:
        print("No rows found for the id")
        return False
    else:
        print("rows:",rows.data)
        return rows.data[0]
    



def update_transcript_pdf_entry(transcript_id, extracted_transcript, extra_text):
    update_document = {
        'extracted_transcript': extracted_transcript,
        'extra_text': extra_text
    }

    result = supabase.table('pdf-transcripts').update(update_document).eq('id', transcript_id).execute()
    print("Updated document:")
    return result


if __name__ == '__main__':
    etitle = 'Frances_Election_Results_Explained'
    # print(get_transcript_row(etitle))
    # print(check_ts_exist(etitle))