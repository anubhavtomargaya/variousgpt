from supabase import create_client, Client
import os
from utils_ts import SUPABASE_URL ,SUPABASE_SERVICE_KEY

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

def check_pdf_exist(company_name, quarter,date, financial_year, doc_type):
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
    
def check_transcript_extracted(file_name):
    existing_ts = supabase.table('pdf-transcripts') \
                          .select('extracted_transcript') \
                          .eq('file_name', file_name) \
                          .execute()
    print("existing extracted_transcript field:", existing_ts)
    if existing_ts.data and existing_ts.data[0]['extracted_transcript'] is not None:
        return True
    else:
        print("transcript doesnt exist")
        return False
    
def insert_initial_transcript_entry(company_name,
                                    quarter, 
                                    date,
                                    file_name,
                                    financial_year,
                                    doc_type,
                                    description,
                                    key_people
                                    ):
    ts_document = {
        'company_name': company_name,
        'quarter': quarter,
        'date':date,
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
    

def get_transcript_row_filename(file_name)->dict:
    rows =  supabase.table('pdf-transcripts').select('*').eq('file_name', file_name).execute()
    if not rows.data:
        print("No rows found for the id")
        return False
    else:
        print("rows:",rows.data)
        return rows.data[0]
    



def update_transcript_pdf_entry(file_name, extracted_transcript, extra_text):
    try:
        update_document = {
        'extracted_transcript': extracted_transcript,
        'extra_text': extra_text
        }

        result = supabase.table('pdf-transcripts').update(update_document).eq('file_name', file_name).execute()
        print("Updated transcript!:",result)
        return result.data
    except Exception as e:
        print("Excepion in update transcript,",e.__str__())
        return False 

if __name__ == '__main__':
    etitle = 'Frances_Election_Results_Explained'
    # print(get_transcript_row(etitle))
    # print(check_ts_exist(etitle))