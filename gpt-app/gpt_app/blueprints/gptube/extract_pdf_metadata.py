import json
from typing import Dict
import fitz

from gpt_app.common.supabase_handler import check_pdf_exist,insert_initial_transcript_entry
from gpt_app.common.utils_openai import count_tokens,get_openai_client

openai_client = get_openai_client()

def extract_text_from_pdf(pdf_path: str, num_pages: int = 2) -> str:
    """
    Extract text from the first n pages of a PDF file.
    """
    try:
        doc = fitz.open(pdf_path)
        doc = fitz.open(pdf_path)
        text = ""
        for i in range(min(num_pages, len(doc))):
            text += doc[i].get_text()
        doc.close()
        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return None
    
def extract_text_from_pdf_storage(file_storage,num_pages=2):
    document = fitz.open(stream=file_storage.read(), filetype="pdf")
    text = ""

    for page_num in range(min(num_pages, len(document))):
        page = document.load_page(page_num)
        text += page.get_text()

    return text



def extract_metadata(pdf_path: str, num_pages: int = 2) -> Dict:
    print("giving intro to experrrrrrrrt..")
    text = extract_text_from_pdf_storage(pdf_path)
    if not text:
        return {}
    
    prompt = f"""
    Analyze the following text extracted from a document and extract the metadata as specified below. 
    If you can't find a specific piece of information, use None for that field.
    If the document is not a earning concall Transcript then just return an empty dictionary ``
    
    Format the output as a JSON string with the following structure:
    {{
        "company_name": "Name of the company, or None if not found",
        "doc_type": "Type of document (e.g., 'Quarterly Earnings Call Transcript', 'Annual Report', etc.)",
        "doc_name": "make a filename by concating the company name with _ (underscores) and quarter, FY etc to make a unique file name",
        "quarter": "Quarter (Q1, Q2, Q3, or Q4) if applicable, or None",
        "financial_year": "Financial year in format FYxx (e.g., FY24, FY23)",
        "description" :"short description of the document based on your knowledge, write a 350 word passage on what you think the pdf is about",
        "key_people": {{
            "person1": {{"name": "Name of person", "role": "Role/designation"}},
            "person2": {{"name": "Name of person", "role": "Role/designation"}},
            // Add more persons as needed
        }}
    }}
    
    Be sure to:
    1. Identify the company name, which is likely mentioned at the beginning of the document.
    2. Determine the document type based on the content and structure.
    3. Look for mentions of quarters (Q1, Q2, Q3, Q4) and financial years. Return the financial year in xxxx format.
        Event if its mentioned as FY24 for example, return as FY2024.
    4. write a passage that contains the necessary info like what is the doc including metadata and other important info. keep around 350 words
    5. Extract names and roles of key management personnel mentioned in the document.
    6. Use None for any fields where the information is not clearly present in the text.
    
    Text to analyze:
    {text[:4000]}  # Limiting to first 4000 characters to avoid token limits
    """
    PDF_METADATA_MODEL = 'gpt-3.5-turbo'
    tokens = count_tokens(prompt,model=PDF_METADATA_MODEL)
    print("tokens", tokens)
    
    response = openai_client.chat.completions.create(
        model=PDF_METADATA_MODEL,
        response_format={ "type": "json_object" },
        temperature=0.4,
        messages=[{"role": "user", "content": prompt}]
    )
    
    try:
        return json.loads(response.choices[0].message.content)
    except json.JSONDecodeError:
        print(f"Error decoding JSON: {response.choices[0].message.content}...")
        return {}

def service_extract_pdf_metadata(fl):
    
    metadata = extract_metadata(fl)
    # print(json.dumps(metadata, indent=2)) 
    print("metadata.__dict__")
    print(metadata)
    reques = {
        "company_name":metadata['company_name'],
        "doc_type":metadata['doc_type'],
        "financial_year":metadata['financial_year'],
        "quarter":metadata['quarter'],
        }
    existing= check_pdf_exist(**reques)
    if not existing:
        entry =    {
            "company_name":metadata['company_name'],
            "quarter":metadata['quarter'],
            "financial_year":metadata['financial_year'],
            "doc_type":metadata['doc_type'],
            "description":metadata['description'],
            "key_people":metadata['key_people'],
        
         }
        row_id = insert_initial_transcript_entry(**entry)
        print("new row id",row_id)
        return row_id

    else:
        print("existing",existing)
        return existing['id']


if __name__ == "__main__":
    # fl = "EASEMYTRIP_30052022232300_Transcript3.pdf"
    fl = "Tata Consumer q4 concall.pdf"
    def test_extract_meta():
        metadata = extract_metadata(fl)
        # print(json.dumps(metadata, indent=2)) 
        return metadata
    
    def test_check_ts_pdf():
        metadata = extract_metadata(fl)
        # print(json.dumps(metadata, indent=2)) 
        
        reques = {
            "company_name":metadata['company_name'],
            "doc_type":metadata['doc_type'],
            "financial_year":metadata['financial_year'],
            "quarter":metadata['quarter'],
         }
        return check_pdf_exist(**reques)


    def test_insert_pdf_ts_entry():
        metadata = extract_metadata(fl)
        # print(json.dumps(metadata, indent=2)) 
        entry =    {
            "company_name":metadata['company_name'],
            "quarter":metadata['quarter'],
            "financial_year":metadata['financial_year'],
            "doc_type":metadata['doc_type'],
            "description":metadata['description'],
            "key_people":metadata['key_people'],
        
         }
        return insert_initial_transcript_entry(**entry)

    # print(test_extract_meta())
    print(test_check_ts_pdf())
    # print(test_insert_pdf_ts_entry())