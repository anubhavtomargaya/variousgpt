
import json
from utils_ts import get_openai_client,count_tokens
from extract_qa_supabase import get_pdf_chunks_transcript, get_pdf_transcript_and_meta, insert_transcript_intel_entry, update_transcript_meta_entry

QA_START_MODEL = 'gpt-4o-mini'
openai_client = get_openai_client()
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
            print(transcript_json[result])
            # print('bfore')
            # print(transcript_json[str(int(result)-1)])
            # print('after')
            # print(transcript_json[str(int(result)+1)])
            return int(result)

    return None  # If Q&A section start is not found

import json
from openai import OpenAI

def process_transcript_qa_section(transcript_json, qa_start_key):
    def process_chunk(chunk):
        prompt = f"""
        Analyze the following chunk of a Q&A transcript from an earnings call:

        {json.dumps(chunk, indent=2)}

        Convert this into a list of dictionaries with the following format:
        [{{
            'question': {{'id': <question_key>, 'text': <concise_question>, 'speaker': {{'name': <question_asker>,'title':<designation & orgname> }} }},
            'answer': {{'text': <answer_text>, 'speaker': {{ 'name': <answer_giver> , 'title': <designation & orgname>}} }}
        }}]

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
        print(response.choices[0].message.content.strip())
        return json.loads(response.choices[0].message.content.strip())
    print('qas')
    qa_section = {k: v for k, v in transcript_json.items() if int(k) >= int(qa_start_key)}
    
    results = []
    chunk_size = 50  # Process 50 entries at a time
    for i in range(0, len(qa_section), chunk_size):
        chunk = dict(list(qa_section.items())[i:i+chunk_size])
        chunk_results = process_chunk(chunk)['result']
        print("cresi;t",chunk_results
              )
        results.extend(chunk_results)
    print("results,",results)
    return results

def insert_qa_section(file,results:list):
    qa_entry = { 'section_qa':results}
    return insert_transcript_intel_entry(file_name=file,
                                         qa_data=qa_entry)

# def get_analyst_questions(file_name): # being used by /view/ directly
#     qa_json = load_qa_section(file_name)
#     # print(text)
#     qa = [text[x]['chunk']['questions']  for x in text.keys() if text[x]['chunk']['segment']=='QA']
#     questions = [ ]

#     # print("QA",questions)
#     for x in qa:
#         questions.extend(x)
#     if not len(questions) >0:
#         return { 'questions': []}

#     s_prompt = "I will give you a list of questions extracted by an LLM from a transcript text. \
#                 Your job is to filter out the junk questions like 'can you hear me?' etc \
#                 declutter the questions. and return  \
#                 the list of questions in a json { question: '', } similar to the json given by me. "

#     res = gpt_filter_analyst_questions(client=openai_client,text=questions,system_prompt=s_prompt)
#     data = json.loads(res)
#     # print("DATA",data)
#     question_dict = { 'questions':data['questions'], 'raw_questions': questions}
   
#     return question_dict

if __name__=='__main__':
    # f = 'fy-2022_q3_earnings_call_transcript_pcbl_limited.pdf'
    f = 'fy25_q1_earnings_call_transcript_zomato_limited_zomato.pdf'
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
    #w2
    def test_get_ts_and_meta():
        data = get_pdf_transcript_and_meta(f)
        key = data['addn_meta']['qa_start_key']
        d = data['extracted_transcript']
        return key,d

    def test_format_qa_section():
        data = get_pdf_transcript_and_meta(f)
        key = data['addn_meta']['qa_start_key']
        d = data['extracted_transcript']
        processed_qa = process_transcript_qa_section(d, key)
        with open('sam_ttl.json','w') as  fl:
            json.dump(processed_qa,fl) 
        return processed_qa
    
    def test_insert_qa_section_intel():
        data = get_pdf_transcript_and_meta(f)
        key = data['addn_meta']['qa_start_key']
        d = data['extracted_transcript']
        processed_qa = process_transcript_qa_section(d, key)
        return insert_qa_section(f,processed_qa)
        
    # print(test_get_ts_chunks())
    # print(test_get_qa_start())
    # print(test_update_qa_start_meta())
    # print(test_get_ts_and_meta())
    print(test_insert_qa_section_intel())
    # print(test_format_qa_section())