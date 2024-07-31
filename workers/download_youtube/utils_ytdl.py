from pathlib import Path

def _make_file_path(direcotry:Path,
                    file_name:Path,
                    format:str=None,
                    local=True):
    if not format:
        format = Path(file_name).as_posix().split('.')[-1]
    file_ = f"{Path(file_name).stem}.{format}"
    if local:
        return Path(direcotry,file_)
    else:
        parts = direcotry.parts
        if not "data" in parts:
            raise ValueError("DATA DIR not found in path")
        
        data_index = parts.index("data")
        after_data = "/".join(parts[data_index:])

        return f"{after_data}/{file_}"
    
    

def upload_blob_to_gcs_bucket_by_filename(gcs_client,
                            source_filepath:Path,
                            dest_dir:Path=None,
                            bucket=BUCKET_NAME,
                            format=None,
                            data=None
                            
                              ):
    bucket = gcs_client.bucket(bucket)
    src_file = Path(source_filepath).stem
    print("FILNEAME",src_file )
    destination_blob_name = _make_file_path(dest_dir,
                                            src_file,
                                            format=format,
                                            local=False)
    print("DESTBLOB",destination_blob_name)
    blob = bucket.blob(destination_blob_name)
    
    if blob.exists():
        return destination_blob_name
    if not data:
        upload = blob.upload_from_filename(Path(source_filepath).__str__())
    else:
        upload = blob.upload_from_string(str(data))
    print("uploaded:",upload)
    print("gcs name,",destination_blob_name)
    exists = blob.exists()
    print(f"Upload successful: {exists}")
    return destination_blob_name
