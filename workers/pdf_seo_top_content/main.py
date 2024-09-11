
 
from pathlib import Path
from generate_content import service_extract_seo_top_questions

def generate_content_valid_pdf(event, context=None):
    print("Processing file")
    if not isinstance(event,dict):
        request_json = event.get_json()
        file_name = request_json['name']
    else:
        file_path = event['name']
        file_name = Path(file_path).name
        # bucket_name = event['bucket']
    try:
     
        print("running top qa for file:",file_name)
        r = service_extract_seo_top_questions(file_name=file_name)
        print(r)
        return True
    except Exception as e:
        print("error in processing pdf",e)
        return False
    