
import json
from typing import Dict, List, Optional

from utils_qa import get_openai_client,count_tokens
from handler_supabase import fetch_management_data, get_pdf_transcript_and_meta, insert_transcript_intel_entry, update_transcript_intel_entry, update_transcript_meta_entry
from utils_qa import load_ts_section_management
from generate_concall_summary_parent import generate_structured_summary
from summary_mg import insert_management_intel

SUMMARY_MODEL = 'gpt-4o-mini'
openai_client = get_openai_client()

def identify_transcript_tags(transcript_json: Dict[str, Dict[str, str]]) -> Dict[str, List[str]]:
    def process_transcript(transcript: Dict[str, Dict[str, str]]) -> Dict:
        transcript_chunks = {
            chunk_id: chunk["text"]
            for chunk_id, chunk in transcript.items()
        }
        
        prompt = f"""
        Review these transcript chunks and categorize them into one of these specific tags:
        - Financial Update 

        Transcript chunks:
        {json.dumps(transcript_chunks)}

        IMPORTANT: DO NOT use "tag_name" as the key. Use one of the exact tags listed above based on the content.
        Each chunk should be assigned to the most relevant tag.
        Respond in JSON format only.

        Required format example:
        {{
            "identified_tags": {{
                "Financial Update": ["2", "3"],
                
                ...
            }}
        }}
        """

        response = openai_client.chat.completions.create(
            model=SUMMARY_MODEL,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": "You are a financial analyst. Use the exact tag names provided ( Financial Update, Challenges etc) to categorize the content. Do not use generic keys like 'tag_name'."
                },
                {"role": "user", "content": prompt}
            ]
        )

        print('res', response.choices[0].message)
        return json.loads(response.choices[0].message.content)

    result = process_transcript(transcript_json)
    return result["identified_tags"]


if __name__ =='__main__':
    # f = 'fy25_q1_earnings_call_transcript_zomato_limited_zomato.pdf'
    f = 'fy-2022_q3_earnings_call_transcript_pcbl_limited.pdf'
    f = 'fy-2024_q1_earnings_call_transcript_neuland_laboratories_524558.pdf'
    # f = 'fy2024_q2_gravita_india_limited_quarterly_earnings_call_transcript_gravita.pdf'
    # f = 'fy2025_q1_pondy_oxides_and_chemicals_limited_quarterly_earnings_call_transcript_pocl.pdf'
    # f = 'fy-2025_q1_earnings_call_transcript_asian_paints_500820.pdf'
    
    def test_management_tags_idfication():
        section = load_ts_section_management(f)
        return identify_transcript_tags(section)
    

    def test_insert_management_tags():
        key = 'tags'
        section = load_ts_section_management(f)
        s = identify_transcript_tags(section)
        if s:
            print("inserting")
            return insert_management_intel(f,key,s)
        else:
            print("not found")
            return None
    
   
    
    print(test_management_tags_idfication())
    print(test_insert_management_tags())