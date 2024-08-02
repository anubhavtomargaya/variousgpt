# import json
# import fitz
# import os
# import openai
# from utils_ts import get_openai_client
# from process_pdf_text import count_tokens
# def extract_text_from_pdf(pdf_path):
#     """
#     Extract text from the first page of a PDF file.
#     """
#     try:
#         doc = fitz.open(pdf_path)
#         first_page = doc[0]
#         text = first_page.get_text()
#         doc.close()
#         return text
#     except Exception as e:
#         print(f"Error extracting text from PDF: {e}")
#         return None

# openai_client = get_openai_client()

# def is_india_concall_transcript(text, filename):
#     prompt = f"""
#                 Analyze the following text and filename to determine if it's a transcript of an earnings call 
#                 for a company listed on the Indian stock market (NSE, BSE). 
                
#                 Text: {text[:1000]}  # Limiting to first 1000 characters
                
#                 Filename: {filename}
                
#                 Respond with only 'True' if it's an earnings call transcript for an Indian listed company, 
#                 or 'False' for anything else.
#                 """
#     tokens = count_tokens(prompt)
#     print("tokens",tokens)
#     response = openai_client.chat.completions.create(
#         model="gpt-4o-mini",
#         temperature=0.4,  
#         messages=[
#             {"role": "system", "content": "You are a financial document analyst."},
#             {"role": "user", "content": prompt}
#             ]
#     )
    
#     try:
#         result = response.choices[0].message.content.strip().lower()
#         return result == 'true'
#     except json.JSONDecodeError:
#         print(f"Error decoding JSON for chunk starting with: {text[:100]}...")
#         print(f"Error decoding JSON : {response.choices[0].message.content}...")
#         return False
    

# def classify_pdf_transcript(pdf_path):
#     """
#     Classify if a PDF is an Indian company earnings call transcript.
#     """
#     filename = os.path.basename(pdf_path)
#     text = extract_text_from_pdf(pdf_path)
    
#     if text is None:
#         return False
    
#     return is_india_concall_transcript(text, filename)

# if __name__ == "__main__":
#     fl = "EASEMYTRIP_30052022232300_Transcript3.pdf"
#     # fl = "Tata Consumer q4 concall.pdf"
#     def test_classify():
#         result = classify_pdf_transcript(fl)
#         print(f"Is Indian company earnings call transcript: {result}")
#         return result

#     print(test_classify())