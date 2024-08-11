# create summary of 
#   - the whole call - using chain of density summary tool
#   - or individual segments (mgmt, qa summaries)
    # format full summary from the two section summaries

# store in the same table another key in the json.



import json
from typing import Dict, List, Optional

from utils_qa import get_openai_client,count_tokens
from handler_supabase import get_pdf_transcript_and_meta, insert_transcript_intel_entry, update_transcript_intel_entry, update_transcript_meta_entry
from utils_qa import load_ts_section_management

SUMMARY_MODEL = 'gpt-4o-mini'
openai_client = get_openai_client()


def summarize_management_guidance(transcript_json: Dict[str, Dict[str, str]]) -> Optional[str]:


    def process_chunk(chunk: Dict[str, Dict[str, str]]) -> Dict:
        prompt = f"""
        Analyze the following chunk of a transcript from an earnings call:

        {json.dumps(chunk, indent=2)}

        Determine if this chunk contains management overview or guidance. If it does, provide a comprehensive summary of the management guidance in 400-500 words. If it doesn't contain management guidance, respond with "No management guidance found."

        Guidelines:
        1. Focus on key points related to the company's future plans, strategies, and financial outlook.
        2. Include specific metrics, targets, or projections mentioned by the management.
        3. Highlight any significant changes in the company's direction or focus.
        4. Mention any challenges or opportunities the management discusses.
        5. If multiple speakers contribute to the guidance, combine their insights into a cohesive summary.

        Return the result as a valid JSON string with the following format:
        {{
            "contains_guidance": true/false,
            "summary": "<400-500 word summary if guidance is found, otherwise null>"
        }}
        """
        print("tokens",count_tokens(prompt,SUMMARY_MODEL))
        response = openai_client.chat.completions.create(
            model=SUMMARY_MODEL,
            response_format={"type":'json_object'},
            messages=[
                {"role": "system", "content": "You are a financial transcript analyzer specializing in management guidance."},
                {"role": "user", "content": prompt}
            ]
        )
        print('res',response.choices[0].message)
        return json.loads(response.choices[0].message.content)

    # Process the entire transcript as one chunk
    result = process_chunk(transcript_json)

    if result['contains_guidance']:
        print("guidance")
        return result['summary']
    else:
        print("no guidance")
        return None
    
def insert_summary_management(file,mg_summary_guidance:list):
    mg_entry =  {'overview':mg_summary_guidance}
    return update_transcript_intel_entry(file_name=file,
                                         mg_data=mg_entry)
if __name__ =='__main__':
    # f = 'fy25_q1_earnings_call_transcript_zomato_limited_zomato.pdf'
    f = 'fy-2022_q3_earnings_call_transcript_pcbl_limited.pdf'
    f = 'fy-2024_q1_earnings_call_transcript_neuland_laboratories_524558.pdf'

    def test_management_content_get():
        return load_ts_section_management(f)
    
    def test_management_content_summary_idfication():
        section = load_ts_section_management(f)
        return summarize_management_guidance(section)
    
    def test_insert_management_content():
        section = load_ts_section_management(f)
        s = summarize_management_guidance(section)
        if s:
            print("inserting")
            return insert_summary_management(f,s)
        else:
            print("not found")
            return None
    
    # print(test_management_content_get())
    # print(test_management_content_summary_idfication())
    print(test_insert_management_content())