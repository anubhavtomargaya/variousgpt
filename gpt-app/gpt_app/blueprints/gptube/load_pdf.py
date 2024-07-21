from werkzeug.utils import secure_filename


from .helpers_gcs import  upload_file_to_gcs, download_gcs_file_as_bytes
from gpt_app.common.dirs import PDF_DIR,TS_DIR
from gpt_app.common.utils_dir import _make_file_path


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