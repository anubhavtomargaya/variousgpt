from werkzeug.utils import secure_filename
from .service_upload_to_gcs import upload_file_to_gcs
from gpt_app.common.dirs import PDF_DIR,BUCKET_NAME
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