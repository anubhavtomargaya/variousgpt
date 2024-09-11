# gcs_utils.py
from pathlib import Path
from google.cloud import storage
import os
ROOT_DIR = Path(__file__).parent.absolute()
CONST_DIR = Path(ROOT_DIR,'constants')
# Initialize the Google Cloud Storage client
storage_client = storage.Client.from_service_account_json(Path(CONST_DIR,Path(f'sa_gcs.json')))

# Replace with your actual bucket name
BUCKET_NAME = 'send-to-car'


def upload_blob(source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print(f"File {source_file_name} uploaded to {destination_blob_name}.")
    
    # Make the blob publicly readable
    blob.make_public()
    
    return blob.public_url

def delete_blob(blob_name):
    """Deletes a blob from the bucket."""
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(blob_name)
    blob.delete()

    print(f"Blob {blob_name} deleted.")

def list_blobs():
    """Lists all blobs in the bucket."""
    bucket = storage_client.bucket(BUCKET_NAME)
    blobs = bucket.list_blobs()

    for blob in blobs:
        print(blob.name)

def blob_exists(blob_name):
    """Check if a blob exists in the bucket."""
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(blob_name)
    return blob.exists()

def get_blob_url(blob_name):
    """Get the public URL for a blob."""
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(blob_name)
    return blob.public_url