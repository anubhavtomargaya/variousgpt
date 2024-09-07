import json
import fitz
import os
import openai
from utils_ts import get_openai_client,count_tokens

def extract_top_text_from_pdf(pdf_path,pg=0):
    """
    Extract text from the first page of a PDF file.
    """
    try:
        doc = fitz.open(pdf_path)
        top_pages = doc[0:pg]
        print("top pages!")
        print(top_pages)
        print(top_pages[0])
        print(top_pages[0].get_text())
        text = ' '.join([ page.get_text() for page in top_pages ])
        print(text)
        doc.close()
        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return None

def extract_bottom_text_from_pdf(pdf_path,pg=0):
    """
    Extract text from the first page of a PDF file.
    """
    try:
        doc = fitz.open(pdf_path)
        first_page = doc[-pg:-1]
        text = first_page.get_text()
        doc.close()
        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return None

openai_client = get_openai_client()
def is_india_concall_transcript(text, filename):
    prompt = f"""
            Analyze the following text extracted from a document and extract the metadata as specified below. 
            If you can't find a specific piece of information, use None for that field.
            If the document is not a earning concall Transcript then just return an empty dictionary {{}}
            
            Format the output as a JSON string with the following structure:
            {{
                "company_name": "Name of the company. ",
                "doc_type": "Type of document (e.g., 'Quarterly Earnings Call Transcript', 'Annual Report', etc.)",
                "date": "Date of event mentioned specifically in the document, format- 'YYYY-MM-DD'",
                "quarter": "Quarter (Q1, Q2, Q3, or Q4) if applicable, or None",
                "financial_year": "Financial year in format FYxx (e.g., FY24, FY23)",
                "nse_scrip_code": string   // NSE ticker symbol as TEXT not the number. (if available, else empty string),
                "bse_scrip_code": string   // BSE ticker symbol . (if available, else empty string),
                "description": "short description of the document based on your knowledge, write a 350 word passage on what you think the pdf is about",
                "key_people": {{
                    "person1": {{"name": "Name of person", "role": "Role/designation"}},
                    "person2": {{"name": "Name of person", "role": "Role/designation"}},
                    // Add more persons as needed
                }}
            }}
            
            Be sure to:
            1. Identify the company name, which is likely mentioned at the beginning of the document. Make sure to include Limited or any other words if it has.
            2. Determine the document type based on the content and structure. As well as the date of event mentioned in the doc,
            3. Look for mentions of quarters (Q1, Q2, Q3, Q4) and financial years. Return the financial year in xxxx format.
                Event if its mentioned as FY24 for example, return as FY2024. If the quarter is not mentioned specifically as Q1, Q2 etc then use the date to guess the quarter. 
                follow the standard financial year naming starting in April as Q1. Example; if the date is 29th July, 2024 then concall would be of April-June period, the Quarter And FY would become Q1FY2025.
            4. write a passage that contains the necessary info like what is the doc including metadata and other important info. keep around 350 words
            5. Extract names and roles of key management personnel mentioned in the document.
            6. Use None for any fields where the information is not clearly present in the text.
            
            Text to analyze:
            {text[:10000]}  # Limiting to first 10000 characters to avoid token limits
            """
    CLASSIFICATION_MODEL = 'gpt-4o-mini'
    tokens = count_tokens(prompt)
    print("tokens", tokens)
    response = openai_client.chat.completions.create(
        model=CLASSIFICATION_MODEL,
        temperature=0.3,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": "You are a financial document analyst. Respond with a JSON object exactly as specified."},
            {"role": "user", "content": prompt}
        ]
    )
    
    try:
        result = json.loads(response.choices[0].message.content)
        if result:  # If the result is not an empty dictionary
            # Ensure financial_year is in the correct format
            if result.get("financial_year") and len(result["financial_year"]) == 4:
                result["financial_year"] = f"FY{result['financial_year']}"
            
            # Construct filename if not already present
            if "doc_name" not in result or not result["doc_name"]:
                filename_parts = [
                    str(result.get("financial_year", "")).lower(),
                    str(result.get("quarter", "")).lower(),
                    str(result.get("company_name", "")).lower().replace(" ", "_"),
                    str(result.get("doc_type", "").replace(" ", "_")).lower(),
                    str(result.get("nse_scrip_code", "")).lower()
                ]
                result["doc_name"] = "_".join(filter(None, filename_parts)) + ".pdf"
        
        return result
    except json.JSONDecodeError:
        print(f"Error decoding JSON for chunk starting with: {text[:100]}...")
        print(f"Error decoding JSON: {response.choices[0].message.content}...")
        return {}
    
def classify_pdf_transcript(pdf_path):
    """
    Classify if a PDF is an Indian company earnings call transcript.
    """
    filename = os.path.basename(pdf_path)
    text = extract_top_text_from_pdf(pdf_path,pg=2)
    
    if text is None:
        return False
    
    return is_india_concall_transcript(text, filename)

if __name__ == "__main__":
    # fl = "EASEMYTRIP_30052022232300_Transcript3.pdf"
    # fl = "Tata Consumer q4 concall.pdf"
    fl = 'Earnings-Call-Transcript-Q1-FY-2021.pdf'
    def test_classify():
        result = classify_pdf_transcript(fl)
        print(f"Is Indian company earnings call transcript: {result}")
        return result

    
    print(test_classify())