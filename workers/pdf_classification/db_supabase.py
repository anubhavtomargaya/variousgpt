from supabase import create_client, Client
import os
from typing import Optional
from utils_ts import SUPABASE_URL ,SUPABASE_SERVICE_KEY

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)


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
    
def insert_classifier_entry(import_filename,given_filename,file_metadata={}):

    classifier_doc = {
            
        
            'import_filename': import_filename,
            'given_file_name': given_filename,
            'file_metadata': file_metadata,
            'classifier_version':'v0'
        }

        # Insert user into the users table
    supabase.table('pdf-classification').insert(classifier_doc).execute()
    return True 

def validate_company_data(company_name: str, ticker: str) -> bool:
    """
    Validates if company name and ticker exist in company-data table
    Returns True if found, False otherwise
    """
    try:
        result = supabase.table('company-data')\
            .select('*')\
            .or_(f"company_name.eq.{company_name},ticker.eq.{ticker}")\
            .execute()
        
        return bool(result.data)
    except Exception as e:
        print("Exception in supabse, %s",e)
        
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
                                    date,
                                    ticker,
                                    file_name,
                                    financial_year,
                                    doc_type,
                                    description,
                                    key_people,
                                    addn_meta
                                    ):
    ts_document = {
        'company_name': company_name,
        'quarter': quarter,
        'date':date,
        'ticker':ticker,
        'file_name':file_name,
        'financial_year': financial_year,
        'doc_type': doc_type,
        'description': description,
        'key_people': key_people,
        'addn_meta':addn_meta,
    }

    result = supabase.table('pdf-transcripts').insert(ts_document).execute()
    # print("Inserted document:", result)
    return result.data[0]['id'] if result.data else None  

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

def update_transcript_meta(file_name, key,value):
    # First, fetch the existing record to get current metadata
    existing_record = supabase.table('pdf-transcripts').select('addn_meta').eq('file_name', file_name).execute()
    
    # Get existing additional metadata or initialize empty dict if none exists
    current_addn_meta = existing_record.data[0].get('addn_meta', {}) if existing_record.data else {}
    
    # Update the metadata with new website URL while preserving existing entries
    current_addn_meta[key] = value
    
    meta = {
        'addn_meta': current_addn_meta
    }

    result = supabase.table('pdf-transcripts').update(meta).eq('file_name', file_name).execute()
    print("Updated document:", result)
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