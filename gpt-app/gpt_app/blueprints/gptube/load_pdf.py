import requests
from werkzeug.utils import secure_filename
from tempfile import NamedTemporaryFile
from .helpers_gcs import  upload_file_to_gcs, download_gcs_file_as_bytes
from gpt_app.common.dirs import PDF_DIR,TS_DIR
from gpt_app.common.utils_dir import _make_file_path


def load_pdf_link_into_bucket(pdf_link):
    try:
        response = requests.get(pdf_link,timeout=15)
        print("response ")
        print(response)
        print(response.content)
        response.raise_for_status()  # Ensure the request was successful

        if 'application/pdf' in response.headers.get('Content-Type', ''):
            # Use a temporary file to store the downloaded PDF
            with NamedTemporaryFile(delete=False) as tmp_file:
                tmp_file.write(response.content)
                tmp_file.flush()
                tmp_file.seek(0)

                # Create a filename from the link
                filename = pdf_link.split('/')[-1]
                if not filename.endswith('.pdf'):
                    filename += '.pdf'
                filename = secure_filename(filename)

                # Upload the temporary file to GCS
                destination_blob_name = _make_file_path(PDF_DIR, filename, local=False)
                file_url = upload_file_to_gcs(tmp_file, destination_blob_name)

            return file_url
        else:
            raise Exception("Provided link does not contain a PDF file")
    
    except requests.exceptions.RequestException as e:
        raise Exception("LoadError: couldn't download PDF from link: %s" % e.__str__())
    except Exception as e:
        raise Exception("LoadError: couldn't upload PDF from link: %s" % e.__str__())
    
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'pdf'

def load_pdf_into_bucket(file):
    try:
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            destination_blob_name = _make_file_path(PDF_DIR,
                                                filename,local=False)
            file_url = upload_file_to_gcs(file, destination_blob_name)
            return file_url
    except Exception as e:
        raise Exception("LoadError: couldnt upload pdf : %s",e.__str__())
    
def download_pdf_from_bucket(file_name, dir=PDF_DIR,format='pdf'):
    source_blob_name = _make_file_path(direcotry=dir,file_name=file_name,
                                       local=False,format=format)   
 
    return download_gcs_file_as_bytes(source_blob_name=source_blob_name)

def download_transcript_json_from_bucket(file_name, dir=TS_DIR):
    source_blob_name = _make_file_path(direcotry=dir,file_name=file_name,format='json',
                                       local=False)   
    
    return download_gcs_file_as_bytes(source_blob_name=source_blob_name)