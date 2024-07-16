import fitz 
# import PyPDF2


# def extract_text_from_pdf(pdf_path):
#     """Extract text from a PDF file."""
#     with open(pdf_path, 'rb') as file:
#         reader = PyPDF2.PdfFileReader(file)
#         text = ""
#         for page_num in range(reader.numPages):
#             page = reader.getPage(page_num)
#             text += page.extract_text()
#     return text

def extract_text_from_pdf_bytes(pdf_bytes):
    """Extracts text from a PDF file in memory."""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    text = ""
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text += page.get_text()
    return text