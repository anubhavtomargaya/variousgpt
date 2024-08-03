import os
from pathlib import Path
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from tempfile import NamedTemporaryFile
from werkzeug.utils import secure_filename
import ssl
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# Suppress only the single InsecureRequestWarning from urllib3 needed to handle SSL certificate issues
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

from .helpers_gcs import  upload_file_to_gcs, download_gcs_file_as_bytes
from gpt_app.common.dirs import PDF_DIR,TS_DIR
from gpt_app.common.utils_dir import _make_file_path


def load_pdf_link_into_bucket(pdf_link):
    try:
        # Create a session to persist parameters across requests
        session = requests.Session()
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        session.mount('https://', HTTPAdapter(max_retries=retries))
        
        # Make the request with verification disabled to handle SSL certificate issues
        response = session.get(pdf_link, timeout=15, verify=False)
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
        raise Exception("LoadError: couldn't download PDF from link: %s" % str(e))

    # except requests.exceptions.RequestException as e:
    #     raise Exception("LoadError: couldn't download PDF from link: %s" % e.__str__())
    # except Exception as e:
    #     raise Exception("LoadError: couldn't upload PDF from link: %s" % e.__str__())
    
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'pdf'

def load_pdf_into_bucket(file,destination_filename,bucket=None):
    try:
        print('loading in bucket',bucket,file)
        print('loading in bucket dest',destination_filename)
        if file:
            filename = Path(destination_filename)
            destination_blob_name = _make_file_path(PDF_DIR,
                                                filename,format='pdf',local=False)
            with open(file,'rb') as tmpfile:
                file_url = upload_file_to_gcs(tmpfile, destination_blob_name,bucket=bucket)
                return file_url
        else:
            raise Exception("Loaderror",file,allowed_file(destination_filename ))
    except Exception as e:
        raise Exception("LoadError: couldnt upload pdf : %s",e.__str__())
    
    
def download_pdf_from_bucket(file_name, dir=PDF_DIR,format='pdf',bucket=None):
    source_blob_name = _make_file_path(direcotry=dir,file_name=file_name,
                                       local=False,format=format)   
 
    return download_gcs_file_as_bytes(source_blob_name=source_blob_name,bucket=bucket)

BUCKET_NAME = 'gpt-app-data'
# BUCKET_NAME = 'pdf-transcripts'
# # gcs_client = storage.Client()
# gcs_client = storage.Client.from_service_account_json(Path(f'sa_gcs.json'))
from  gpt_app.blueprints.gptube.helpers_gcs import download_gcs_file

def download_pdf_from_pdf_bucket_file(file_name, dir=PDF_DIR,format='pdf',bytes=False,bucket=None):
    source_blob_name = _make_file_path(direcotry=dir,file_name=file_name,
                                       local=False,format=format)   
    if bytes:
        return download_gcs_file_as_bytes(source_blob_name=source_blob_name)
    else:
        print("makking tmp path",file_name) 
        destination_file_path = os.path.join('/tmp', f"{file_name}.pdf")
        return download_gcs_file(source_blob_name,destination_file_name=destination_file_path,bucket=bucket)
    
def download_transcript_json_from_bucket(file_name, dir=TS_DIR):
    source_blob_name = _make_file_path(direcotry=dir,file_name=file_name,format='json',
                                       local=False)   
    
    return download_gcs_file_as_bytes(source_blob_name=source_blob_name)