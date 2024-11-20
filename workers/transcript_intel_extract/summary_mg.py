# create summary of 
#   - the whole call - using chain of density summary tool
#   - or individual segments (mgmt, qa summaries)
    # format full summary from the two section summaries

# store in the same table another key in the json.



import json
from typing import Dict, List, Optional

from utils_qa import get_openai_client,count_tokens
from handler_supabase import fetch_addn_metadata, fetch_management_data, get_pdf_transcript_and_meta, insert_transcript_intel_entry, update_transcript_intel_entry, update_transcript_meta_entry
from utils_qa import load_ts_section_management

SUMMARY_MODEL = 'gpt-4o-mini'
openai_client = get_openai_client()

def insert_management_intel(file: str,
                            key:str,
                            document: dict,
                            prompt=None,
                            prompt_version=None) -> str:
    if not isinstance(document, dict):
        raise TypeError("Tags must be a dictionary")
    
    current_mg_data = fetch_management_data(file)
    current_addn_meta = fetch_addn_metadata(file)
    print("current_data exist")
    # Add the new tags to the management_data
    current_mg_data[key] = document
    current_addn_meta[key] =   {"prompt_name":prompt,"prompt_version":prompt_version}
    # Update the database with the new management_data
    return update_transcript_intel_entry(file_name=file, mg_data=current_mg_data,adn_meta=current_addn_meta)


if __name__ =='__main__':
    # f = 'fy25_q1_earnings_call_transcript_zomato_limited_zomato.pdf'
    f = 'fy-2022_q3_earnings_call_transcript_pcbl_limited.pdf'
    f = 'fy-2024_q1_earnings_call_transcript_neuland_laboratories_524558.pdf'
    # f = 'fy2024_q2_gravita_india_limited_quarterly_earnings_call_transcript_gravita.pdf'
    # f = 'fy2025_q1_pondy_oxides_and_chemicals_limited_quarterly_earnings_call_transcript_pocl.pdf'
    # f = 'fy-2025_q1_earnings_call_transcript_asian_paints_500820.pdf'

    def test_management_content_get():
        return load_ts_section_management(f)
    
    
    
    # print(test_management_content_get())

    # print(test_insert_management_tags())
    # print(test_management_content_summary_idfication())