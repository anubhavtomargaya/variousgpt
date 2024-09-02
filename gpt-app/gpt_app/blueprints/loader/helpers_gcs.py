from  gpt_app.common.utils_dir import client as gcs_client

# BUCKET_NAME = 'gpt-app-data'
BUCKET_NAME = 'pdf-transcripts'

def upload_file_to_gcs(file,
                        filename,
                        bucket=BUCKET_NAME):
    storage_client = gcs_client
    print("uploading file to gcs",file)
    bucket = storage_client.bucket(bucket)
    blob = bucket.blob(filename)
    print("blob",blob)
    blob.upload_from_file(file)
    return blob.public_url

def upload_data_to_gcs(data,
                       destination_blob_name,
                       bucket=BUCKET_NAME,
                       ):
    bucket = gcs_client.bucket(BUCKET_NAME)
    blob = bucket.blob(destination_blob_name)
    if blob.exists():
        print("blob exists")
        return False
    upload = blob.upload_from_string(data)
    print("gcs up,",upload)
    return blob.public_url

def download_gcs_file_as_bytes(source_blob_name,bucket=None):
    bucket = gcs_client.bucket(bucket)
    blob = bucket.blob(source_blob_name)
    print(blob)
    return blob.download_as_bytes()

def download_gcs_file(source_blob_name, destination_file_name,bucket=BUCKET_NAME):
    bucket = gcs_client.bucket(bucket)
    blob = bucket.blob(source_blob_name)
    with open(destination_file_name, 'wb') as file_obj:
        blob.download_to_file(file_obj)
    print("file downloaded",destination_file_name)
    return destination_file_name
# def download_gcs_file(source_blob_name, destination_file_name):
#     bucket = gcs_client.bucket(BUCKET_NAME)
#     blob = bucket.blob(source_blob_name)
#     print(blob)
#     blob.download_to_filename(destination_file_name)
#     return True