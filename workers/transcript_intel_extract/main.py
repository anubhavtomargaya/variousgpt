
import json
from pathlib import Path
from typing import Any, Dict
from utils_qa import get_openai_client,count_tokens, insert_qa_section, load_ts_section_management
from handler_supabase import ( 
                                get_pdf_chunks_transcript,
                                get_pdf_transcript_and_meta, 
                                update_transcript_meta_entry
                            )
from summary_mg import insert_summary_management, summarize_management_guidance

QA_START_MODEL = 'gpt-4o-mini'
openai_client = get_openai_client()


#w1
def find_qa_section_start(transcript_json, openai_client):
    def process_chunk(chunk):
        prompt = f"""
        Analyze the following chunk of a transcript from an earnings call:

        {json.dumps(chunk, indent=2)}

        Identify the key (integer) where the Q&A section begins. 
        The Q&A section typically starts after the management's overview, 
        when the moderator opens the floor for questions from analysts or investors.

        Return only the integer key where the Q&A section starts. 
        If the Q&A section does not start in this chunk, return 'Not found'.
        """
        print("tokens",count_tokens(prompt,model=QA_START_MODEL))
        response = openai_client.chat.completions.create(
            model=QA_START_MODEL,
            temperature=0.2,
            messages=[
                {"role": "system", "content": "You are a financial transcript analyzer."},
                {"role": "user", "content": prompt}
            ]
        )

        return response.choices[0].message.content.strip()

    chunk_size = 20  # Process 20 entries at a time
    for i in range(0, len(transcript_json), chunk_size):
        chunk = dict(list(transcript_json.items())[i:i+chunk_size])
        result = process_chunk(chunk)
        
        if result.isdigit():
            print("yes")
            # print(transcript_json[result])
            # print('bfore')
            # print(transcript_json[str(int(result)-1)])
            # print('after')
            # print(transcript_json[str(int(result)+1)])
            return int(result)

    return None  # If Q&A section start is not found


#w2

def process_transcript_qa_section(transcript_json, qa_start_key):
    def process_chunk(chunk):
        prompt = f"""
        Analyze the following chunk of a Q&A transcript from an earnings call:

        {json.dumps(chunk, indent=2)}

        Convert this into a list of dictionaries with the following format:
        {{"result" : [{{
            'question': {{'id': <question_key>, 'text': <concise_question>, 'speaker': {{'name': <question_asker>,'title':<designation & orgname> }} }},
            'answer': {{'text': <answer_text>, 'speaker': {{ 'name': <answer_giver> , 'title': <designation & orgname>}} }}
        }}]
        }}
        Guidelines:
        1. Extract the question ID (key), make the question text concise by removing phrases like "my next question is" or "I was wondering".
        2. Identify the speaker who asked the question.Along with their title and company name
        3. Extract the full answer given by the management.
        4. Identify the speaker who gave the answer. Along with their title if available, if not then keep it as empty.
        5. If a question has multiple parts or follow-ups, combine them into a single question entry.
        6. If there are multiple speakers answering a question, combine their responses into a single answer entry.

        Return the result as a valid JSON string.
        """

        print("token",count_tokens(prompt,model=QA_START_MODEL))
        response = openai_client.chat.completions.create(
            model=QA_START_MODEL,
             response_format={"type":'json_object'},
            temperature=0.2,
            messages=[
                {"role": "system", "content": "You are a financial transcript analyzer."},
                {"role": "user", "content": prompt}
            ]
        )
        print("repso")
        # print(response.choices[0].message.content.strip())
        return json.loads(response.choices[0].message.content.strip())
    print('qas')
    qa_section = {k: v for k, v in transcript_json.items() if int(k) >= int(qa_start_key)}
    
    results = []
    chunk_size = 50  # Process 50 entries at a time
    for i in range(0, len(qa_section), chunk_size):
        chunk = dict(list(qa_section.items())[i:i+chunk_size])
        chunk_results = process_chunk(chunk)['result']
        print("cresi;t"
              )
        results.extend(chunk_results)
    print("results,")
    # results)
    return results


def process_earnings_call_qa(filename: str) -> Dict[str, Any]:
    try:
        # Step 1: Get transcript chunks
        transcript_json = get_pdf_chunks_transcript(filename)
        if not transcript_json:
            raise ValueError(f"Failed to retrieve transcript chunks for {filename}")

        # Step 2: Find Q&A section start
        qa_start_key = find_qa_section_start(transcript_json, openai_client)
        if qa_start_key is None:
            raise ValueError(f"Failed to find Q&A section start for {filename}")

        # Step 3: Update transcript meta entry with Q&A start key
        update_result = update_transcript_meta_entry(filename, str(qa_start_key))
        if not update_result:
            raise ValueError(f"Failed to update transcript meta entry for {filename}")

        # Step 4: Get updated transcript and meta data
        data = get_pdf_transcript_and_meta(filename)
        if not data or 'extracted_transcript' not in data or 'addn_meta' not in data:
            raise ValueError(f"Failed to retrieve updated transcript and meta data for {filename}")

        # Step 5: Process Q&A section
        qa_section = process_transcript_qa_section(data['extracted_transcript'], qa_start_key)
        if not qa_section:
            raise ValueError(f"Failed to process Q&A section for {filename}")

        # Step 6: Insert processed Q&A section
        insert_result = insert_qa_section(filename, qa_section)
        if not insert_result:
            raise ValueError(f"Failed to insert Q&A section for {filename}")
        
   
      

        return {
            "status": "success",
            "message": f"Successfully processed Q&A section for {filename}",
            "qa_start_key": qa_start_key,
            "qa_section_length": len(qa_section)
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "filename": filename
        }
    

def process_earning_call_summary(file_name):
    try:
        section = load_ts_section_management(file_name)
        if not section:
            raise ValueError(f"Unable to get management section from ts for :{file_name}")
        
        s = summarize_management_guidance(section)
        if s:
            print("inserting")
            s_insert_result =  insert_summary_management(file_name,s)
            print("insert success",s_insert_result)
        else:
            raise ValueError(f"failed to get summary for section  {section}")
        return s_insert_result

    except Exception as e:
        print("Exce",e)
        return False
    

def main_process_qa_fx(event,context=None):
    print("Processing ts intel qa section")
    if not isinstance(event,dict):
        request_json = event.get_json()
        file_name = request_json['name']
      
    else:
        file_path = event['name']
        file_name = Path(file_path).name

        print(f"Processing file: {file_name} in _pdf-transcript_ table")
    qa_proc = process_earnings_call_qa(filename=file_name)
    
    if qa_proc['status']=='success':
        summ_proc = process_earning_call_summary(file_name=file_name)
        if not summ_proc:
            res = 'summary-failure'
        else:
            res = 'summary-success'
        qa_proc["status_addn"] = res
        return qa_proc
       
if __name__=='__main__':
    # f = 'fy-2022_q3_earnings_call_transcript_pcbl_limited.pdf'
    # f = 'fy25_q1_earnings_call_transcript_zomato_limited_zomato.pdf'
    # f = 'fy-2024_q1_earnings_call_transcript_neuland_laboratories_524558.pdf'
    f = 'fy-2024_q4_Earnings_Conference_Raymond Limited.pdf'

    def test_get_ts_chunks():
        ts =  get_pdf_chunks_transcript(f)
        print(ts.keys())
        return ts
    
    def test_get_qa_start():
        transcript_json =  get_pdf_chunks_transcript(f)
        return find_qa_section_start(transcript_json, openai_client)
    
    def test_update_qa_start_meta():
        transcript_json =  get_pdf_chunks_transcript(f)
        start_key  = find_qa_section_start(transcript_json, openai_client)
        return update_transcript_meta_entry(f,str(start_key))
    

    #w2 - tests
    def test_get_ts_and_meta():
        data = get_pdf_transcript_and_meta(f)
        key = data['addn_meta']['qa_start_key']
        d = data['extracted_transcript']
        if not isinstance(d,dict):
            raise Exception("Error in extracted_transcript")
        return key,list(d.keys())

    def test_format_qa_section():
        data = get_pdf_transcript_and_meta(f)
        key = data['addn_meta']['qa_start_key']
        d = data['extracted_transcript']
        processed_qa = process_transcript_qa_section(d, key)
        with open(f'sam_{f}_ttl.json','w') as  fl:
            json.dump(processed_qa,fl) 
        return processed_qa
    
    def test_insert_qa_section_intel():
        data = get_pdf_transcript_and_meta(f)
        key = data['addn_meta']['qa_start_key']
        d = data['extracted_transcript']
        processed_qa = process_transcript_qa_section(d, key)
        return insert_qa_section(f,processed_qa)
        

    #main -tests
    def test_pipeline():
        return process_earnings_call_qa(f)
    # print(test_get_ts_chunks())
    # print(test_get_qa_start())
    # print(test_get_ts_and_meta())
    # print(test_format_qa_section())
    # print(test_update_qa_start_meta())

    # print(test_insert_qa_section_intel())

    print(test_pipeline())