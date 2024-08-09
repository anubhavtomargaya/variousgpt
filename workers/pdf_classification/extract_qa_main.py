
import json
from utils_ts import get_openai_client,count_tokens
from extract_qa_supabase import get_pdf_chunks_transcript, update_transcript_meta_entry

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
    
    # print(test_get_ts_chunks())
    # print(test_get_qa_start())
    print(test_update_qa_start_meta())