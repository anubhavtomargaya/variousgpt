import json
import fitz
import os
from gpt_app.common.utils_openai import count_tokens,get_openai_client

def extract_text_from_pdf(pdf_path):
    """
    Extract text from the first page of a PDF file.
    """
    try:
        doc = fitz.open(pdf_path)
        first_page = doc[0]
        text = first_page.get_text()
        doc.close()
        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return None

openai_client = get_openai_client()

def is_india_concall_transcript(text, filename):
    prompt = f"""
                Analyze the following text and filename to determine if it's a transcript of an earnings call 
                for a company listed on the Indian stock market (NSE, BSE). 
                
                Text: {text[:10000]}  # Limiting to first 10000 characters
                
                Filename: {filename}
                If it is a concall generate a suitable name for it using the 
                
                1. financia lyear in the format FY-YYYY
                2. quarter name (Q1,Q4 etc)
                3. type of document (earnings call transcript, shareholder letter, annual report etc)
                4. COMPANY NAME (Extract using the first few pages given in context above)
                5. COMPANY TICKER (optional, if possible find the ticker that the company has in NSE/BSE if not available skip it)
                Using the above information provide an appropriate name for the pdf file, concat eeverything using "_" (underscores) 

                Respond with ONLY the formulated filename (including extension). AND NOT OTHER TEXT OR MARKDOWN FORMATTING ETC.
                if it's an earnings call transcript for an Indian listed company, 
                or 'False' for anything else.
                """
    CLASSIFICATION_MODEL = 'gpt-4o-mini'
    tokens = count_tokens(prompt)
    print("tokens",tokens)
    response = openai_client.chat.completions.create(
        model=CLASSIFICATION_MODEL,
        temperature=0.4,  
        messages=[
            {"role": "system", "content": "You are a financial document analyst and manage the data storage for the documents."},
            {"role": "user", "content": prompt}
            ]
    )
    
    try:
        result = response.choices[0].message.content.strip().lower()
        return result 
    except json.JSONDecodeError:
        print(f"Error decoding JSON for chunk starting with: {text[:100]}...")
        print(f"Error decoding JSON : {response.choices[0].message.content}...")
        return False
    

def classify_pdf_transcript(pdf_path):
    """
    Classify if a PDF is an Indian company earnings call transcript.
    """
    filename = os.path.basename(pdf_path)
    text = extract_text_from_pdf(pdf_path)
    
    if text is None:
        return False
    
    return is_india_concall_transcript(text, filename)

if __name__ == "__main__":
    fl = "EASEMYTRIP_30052022232300_Transcript3.pdf"
    # fl = "Tata Consumer q4 concall.pdf"
    def test_classify():
        result = classify_pdf_transcript(fl)
        print(f"Is Indian company earnings call transcript: {result}")
        return result

    print(test_classify())