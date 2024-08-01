import fitz
from utils_ts import get_openai_client
def extract_text_with_layout(pdf_bytes):
    """Extracts text from a PDF file in memory along with layout information."""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    pages_text = []

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        blocks = page.get_text("blocks")  # Extract text blocks
        page_text = []

        for block in blocks:
            x0, y0, x1, y1, text, _, _= block
            print('nums')
            print(x0)
            print(y0)
            print(_)
            print(x1)
            print(y1)
            print(text)
            if is_relevant_text(y0, y1, page_num, len(doc)):
                page_text.append(text)

        pages_text.append(" ".join(page_text))

    return " ".join(pages_text).replace('\n', ' ')

def is_relevant_text(y0, y1, page_num, total_pages):
    """Heuristic to filter out headers and footers based on y-coordinates and page position."""
    # Adjust thresholds based on your document's layout
    header_threshold = 600  # Pixels from the top of the page
    footer_threshold = 600  # Pixels from the bottom of the page

    if page_num == 0 or page_num == total_pages - 1:
        # First and last pages might have different layout, adjust accordingly
        return True

    # Filter out text blocks that are likely headers or footers
    return y0 > header_threshold and y1 < (page_num * 792 - footer_threshold)

def extract_text_from_pdf_bytes(pdf_bytes):
    """Extracts text from a PDF file in memory."""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    text = ""
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text += page.get_text("text")
    return text

import fitz
import json
from typing import List, Dict,Generator

import tiktoken
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
    tokens = count_tokens(prompt)
    print("tokens",tokens)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        temperature=0.4,  
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
        for _, entry in chunk.items():
            merged_transcript[str(counter)] = entry
            counter += 1

    return merged_transcript

def extract_transcript_from_pdf(pdf_path: str) -> Dict[str, Dict[str, Dict[str, str]]]:
    result = {"transcript": {}, "extra": ""}
    doc = fitz.open(pdf_path)
    full_text = ""
    transcript_started = False
    
    for page in doc:
        text = page.get_text()
        if not transcript_started:
            prompt = f"Identify if the following text contains the start of a transcript. If it does, return 'START'. If not, return 'NO':\n\n{text}"
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
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
    chunks = chunk_text_generator(full_text)
    # chunks = chunk_text(full_text)  # Or: chunks = chunk_text_generator(full_text)
    turn_counter = 0
    
    for chunk in chunks:
        print("creating transcript for chunk",len(chunk), chunk[:30])
        chunk_result = process_chunk(chunk, turn_counter)
        result["transcript"].update(chunk_result)
        turn_counter += len(chunk_result)
    
    # Sort the transcript by turn number

    result["transcript"] = dict(sorted(result["transcript"].items(), key=lambda x: int(x[0])))
    # result["transcript_processed"] = post_process_transcript(result["transcript"])
    
    return result


if __name__=='__main__':
    fl = "EASEMYTRIP_30052022232300_Transcript3.pdf"
    fl = "Tata Consumer q4 concall.pdf"
    def test_extract_with_layout():
        with open(fl, "rb") as f:
            pdf_bytes = f.read()

        text = extract_text_with_layout(pdf_bytes)
        print(text)

    def test_extract_with_gpt():
        # Usage example
        pdf_path = fl
        transcript_data = extract_transcript_from_pdf(pdf_path)
        print(json.dumps(transcript_data, indent=2))
        with open(f"gpt_1_{fl}.json", 'w') as file:
            json.dump(transcript_data, file, indent=4)

        return transcript_data
    
    print(test_extract_with_gpt())