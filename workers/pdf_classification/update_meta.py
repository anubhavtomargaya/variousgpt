from classify_pdf import classify_pdf_transcript
from db_supabase import get_distinct_transcript_files, update_transcript_meta
from main import download_pdf_from_pdf_bucket_file

#consts.py
APP_BUCKET = 'gpt-app-data'

IMPORT_BUCKET= 'uploads-mr-pdf'
PROC_PDF_BUCKET = 'pdf-transcripts'

files = get_distinct_transcript_files()
for file in files:
    # get new metadata 
    try:
        path = download_pdf_from_pdf_bucket_file(file_name=file,
                                                    bucket=PROC_PDF_BUCKET)
        metadata = classify_pdf_transcript(path)
        # extract relevant key, v from this 
        k = 'website'
        v = metadata.get(k,None)
        print("kv ",k,v)
    
        update = update_transcript_meta(file,k,v)
        print("updated")

    except Exception as e:
        print("exception in %s . %s",file,e.__str__())