from pathlib import Path
import fitz
from utils_ts import get_openai_client
from db_supabase import check_pdf_exist, check_transcript_extracted, get_transcript_row, get_transcript_row_filename,insert_initial_transcript_entry, update_transcript_pdf_entry
import json
from typing import List, Dict,Generator
import tiktoken
import datetime
def count_tokens(text, model="gpt-3.5-turbo"):
    encoding = tiktoken.encoding_for_model(model)
    tokens = encoding.encode(text)
    return len(tokens)

client = get_openai_client()

def chunk_text(text: str, chunk_size: int = 3000, overlap: int = 500) -> List[str]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")
    if overlap >= chunk_size:
        raise ValueError("overlap must be less than chunk_size")
    
    chunks = []
    start = 0
    print("Chunking text")
    while start < len(text):
        end = start + chunk_size
        if end > len(text):
            end = len(text)
        chunk = text[start:end]
        chunks.append(chunk)
        print(f"start: {start}, end: {end}, chunk length: {len(chunk)}")
        start += chunk_size - overlap  # Ensure start always increments
    print("Chunking text done")
    return chunks

def chunk_text_generator(text: str, chunk_size: int = 3000, overlap: int = 200) -> Generator[str, None, None]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")
    if overlap >= chunk_size:
        raise ValueError("overlap must be less than chunk_size")
    
    start = 0
    print("Chunking text")
    while start < len(text):
        end = start + chunk_size
        if end > len(text):
            end = len(text)
        chunk = text[start:end]
        print("yeliding text")
        yield chunk
        print(f"start: {start}, end: {end}, chunk length: {len(chunk)}")
        start += chunk_size - overlap  # Ensure start always increments
    print("Chunking text done")
# MODEL_MAIN = "gpt-3.5-turbo"
MODEL_MAIN = "gpt-4o-mini"
def process_chunk(chunk: str, turn_counter: int) -> Dict[str, Dict[str, str]]:
    prompt = f"""
    Extract the transcript from the following text, identifying speakers and their turns. 
    Format the output as a JSON string with the following structure:
    {{
        "{turn_counter}": {{"speaker": "Speaker Name", "text": "Speaker's text"}},
        "{turn_counter + 1}": {{"speaker": "Next Speaker Name", "text": "Next speaker's text"}},
        ...
    }}
    Remove any irrelevant information such as page numbers, headers, or footers.
    Continue numbering from {turn_counter}.
    Text to process:
    {chunk}
    """
    tokens = count_tokens(prompt,model=MODEL_MAIN)
    print("tokens",tokens)
    response = client.chat.completions.create(
        # model="gpt-3.5-turbo",
        model=MODEL_MAIN,
        temperature=0.4,  
        response_format={ "type": "json_object" },
        messages=[{"role": "user", "content": prompt}]
    )
    
    try:
        return json.loads(response.choices[0].message.content)
    except json.JSONDecodeError:
        print(f"Error decoding JSON for chunk starting with: {chunk[:100]}...")
        print(f"Error decoding JSON : {response.choices[0].message.content}...")
        return {}
    

def post_process_transcript(transcript: Dict[str, Dict[str, str]], chunk_size: int = 10) -> Dict[str, Dict[str, str]]:
    def chunk_transcript(transcript: Dict[str, Dict[str, str]], chunk_size: int) -> List[Dict[str, Dict[str, str]]]:
        chunks = []
        items = list(transcript.items())
        for i in range(0, len(items), chunk_size):
            chunk = dict(items[i:i+chunk_size])
            chunks.append(chunk)
        return chunks

    def process_transcript_chunk(chunk: Dict[str, Dict[str, str]]) -> Dict[str, Dict[str, str]]:
        chunk_str = json.dumps(chunk, indent=2)
        prompt = f"""
        Analyze and improve the following transcript chunk:
        {chunk_str}

        1. Merge consecutive statements from the same speaker into a single entry.
        2. If a speaker is "Unknown" or seems to be a placeholder (e.g., company name), try to infer the correct speaker based on context.
        3. Ensure speaker names are consistent throughout (e.g., use full names or consistent abbreviations).
        3. Ensure speaker names are consistent throughout (e.g., use full names or consistent abbreviations).
        4. Maintain the chronological order of the statements.

        Return the improved transcript chunk as a JSON string with the same structure, but with merged and corrected entries.
        """

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )

        try:
            return json.loads(response.choices[0].message.content)
        except json.JSONDecodeError:
            print(f"Error decoding JSON in post-processing. Using original chunk.",chunk)
            print(f"Error decoding JSON in post-processing. .",response.choices[0].message.content)
            return chunk

    chunks = chunk_transcript(transcript, chunk_size)
    processed_chunks = [process_transcript_chunk(chunk) for chunk in chunks]

    # Merge processed chunks back into a single transcript
    merged_transcript = {}
    counter = 0
    for chunk in processed_chunks:
        print("chunk",chunk)
        for _, entry in chunk.items():
            merged_transcript[str(counter)] = entry
            counter += 1

    return merged_transcript

def extract_transcript_from_pdf(pdf_path: str,csize:int=3000) -> Dict[str, Dict[str, Dict[str, str]]]:
    result = {"transcript": {}, "extra": ""}
    doc = fitz.open(pdf_path)
    full_text = ""
    transcript_started = False
    
    for page in doc:
        text = page.get_text()
        if not transcript_started:
            prompt = f"Identify if the following text contains the start of a transcript. If it does, return 'START'. If not, return 'NO':\n\n{text}"
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                # model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            if response.choices[0].message.content.strip() == "START":
                print("start")
                transcript_started = True
            else:
                print("adding to extra",text)
                result["extra"] += text + "\n"
                continue
        full_text += text + "\n"
    
    # Use either chunk_text or chunk_text_generator here
    # chunks = chunk_text(full_text) 
    chunks = chunk_text_generator(full_text,chunk_size=csize)
    # chunks = chunk_text(full_text)  # Or: chunks = chunk_text_generator(full_text)
    turn_counter = 0
    
    for chunk in chunks:
        print("creating transcript for chunk", chunk[:30])
        chunk_result = process_chunk(chunk, turn_counter)
        result["transcript"].update(chunk_result)
        turn_counter += len(chunk_result)
    
    # Sort the transcript by turn number

    result["transcript"] = dict(sorted(result["transcript"].items(), key=lambda x: int(x[0])))
    # result["transcript_processed"] = post_process_transcript(result["transcript"])
    
    return result

def service_extract_transcript_texts(pdf_path):
    file_name = Path(pdf_path).name
    print("file name in service extract", file_name)
    if not check_transcript_extracted(file_name):
        print("start time")
        print(datetime.datetime.now())
        transcript_data = extract_transcript_from_pdf(pdf_path,csize=8000)
        # print(json.dumps(transcript_data, indent=2))
        entry_up = {"file_name":file_name,
                    "extracted_transcript":transcript_data['transcript'],
                    "extra_text":transcript_data['extra']
                    }
        print("end time")
        print(datetime.datetime.now())
        
        return update_transcript_pdf_entry(**entry_up)
    else:
        print("getting existing rows....")
        return get_transcript_row_filename(file_name)


if __name__=='__main__':
    # fl = "EASEMYTRIP_30052022232300_Transcript3.pdf"
    # fl = "Tata Consumer q4 concall.pdf"
    fl = "Earnings-Call-Transcript-Q1-FY-2021.pdf"
    # def test_extract_with_layout():
    #     with open(fl, "rb") as f:
    #         pdf_bytes = f.read()

    #     text = extract_text_with_layout(pdf_bytes)
    #     print(text)

    # def test_extract_with_gpt():
    #     # Usage example
    #     pdf_path = fl
    #     transcript_data = extract_transcript_from_pdf(pdf_path)
    #     print(json.dumps(transcript_data, indent=2))
    #     with open(f"gpt_2_{fl}.json", 'w') as file:
    #         json.dump(transcript_data, file, indent=4)

    #     return transcript_data
    import datetime
    def test_update_entry_with_transcript_text():
        pdf_path = fl
        if not check_transcript_extracted(pdf_path):
            print(datetime.datetime.now())
            transcript_data = extract_transcript_from_pdf(pdf_path)
            print(json.dumps(transcript_data, indent=2))
            entry_up = {"transcript_id":1,
                        "extracted_transcript":transcript_data['transcript'],
                        "extra_text":transcript_data['extra']
                        }
            print(datetime.datetime.now())
            
            return update_transcript_pdf_entry(**entry_up)
        else:
            return get_transcript_row(1)

    # print(test_extract_with_gpt())
    print(test_update_entry_with_transcript_text())
    