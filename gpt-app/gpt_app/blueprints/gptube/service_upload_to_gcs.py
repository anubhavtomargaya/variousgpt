from  gpt_app.common.utils_dir import client as gcs_client

BUCKET_NAME = 'gpt-app-data'

def upload_file_to_gcs(file,
                        filename,
                        bucket=BUCKET_NAME):
    storage_client = gcs_client
    bucket = storage_client.bucket(bucket)
    blob = bucket.blob(filename)
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
