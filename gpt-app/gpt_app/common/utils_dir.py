
import tempfile
import openai
from  gpt_app.common.dirs import * 
from gpt_app.common.exceptions import MissingStageFile

from pathlib import Path
import json 

def _read_json(file_path:Path):
    if not isinstance(file_path,Path):
        raise TypeError("Need a path to read json")
    with open(file_path, 'r') as fr:
        return json.load(fr)
    

def _save_json(json_data, file_path:Path):
    if not isinstance(file_path,Path):
        raise TypeError("Need a path to read json")
    with open(file_path, 'w') as fw:
        return json.dump(json_data,fw)
    
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
def check_blob(destination_blob_name,gcs_client):
    bucket = gcs_client.bucket(BUCKET_NAME)
    blob = bucket.blob(destination_blob_name)
    exists = blob.exists()
    return exists

def upload_blob_to_gcs_bucket_by_filename(gcs_client,
                            source_filename:Path,
                            source_dir:Path=PROCESSED_DIR,
                            format=None,
                            data=None
                            
                              ):
    bucket = gcs_client.bucket(BUCKET_NAME)
    print("FILNEAME",source_filename )
    destination_blob_name = _make_file_path(source_dir,
                                            source_filename,
                                            format=format,
                                            local=False)
    print("DESTBLOB",destination_blob_name)
    blob = bucket.blob(destination_blob_name)
    
    if blob.exists():
        return destination_blob_name
    if not data:
        upload = blob.upload_from_filename(Path(source_dir,source_filename).__str__())
    else:
        upload = blob.upload_from_string(str(data))
    print("uploaded:",upload)
    print("gcs name,",destination_blob_name)
    exists = blob.exists()
    print(f"Upload successful: {exists}")
    return destination_blob_name

def download_blob_to_tmpfile(gcs_client,
                            source_filename:Path,
                            source_dir:Path=PROCESSED_DIR,
                              ):
    bucket = gcs_client.bucket(BUCKET_NAME)

      # Download the audio file to a temporary file
    blob_path = _make_file_path(source_dir,
                                            source_filename,
                                            local=False)
    print(blob_path)
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        blob = bucket.blob(blob_path)
        exists = blob.exists()
        print(f"Exists: {exists}")
        blob.download_to_filename(temp_file.name)
    return exists

def download_blob_to_memory(gcs_client,
                            source_filename: Path,
                            source_dir: Path = PROCESSED_DIR,
                            fmt=None):
    bucket = gcs_client.bucket(BUCKET_NAME)

    # Create the blob path
    blob_path = _make_file_path(source_dir, source_filename, local=False,
                                format=fmt)
    print(blob_path)
    
    # Get the blob
    blob = bucket.blob(blob_path)
    exists = blob.exists()
    print(f"Exists: {exists}")

    if exists:
        # Download the blob's content as a string
        blob_content = blob.download_as_string()

        # Parse the string content as JSON
        json_content = json.loads(blob_content)
        return json_content
    else:
        return None

def load_summary_embedded(file_name)->dict:
    file_path = Path(EMBEDDING_DIR,f"{Path(file_name).stem}.json")
    with open(file_path, 'r') as fr:
        return json.load(fr)
    
def save_summary(doc, file_name):
     file_path =  Path(SUMMARY_DIR,file_name)
     with open(file_path, 'w') as fw:
        return json.dump(doc,fw)
     
def check_ts_dir(file_name:Path):
    if not isinstance(file_name,Path):
        file_name = Path(file_name)
    file_stem = file_name.stem
    file = Path(TS_DIR,f"{file_stem}.json")
    return file.exists()

def check_summary_dir(file_name:Path):
    if not isinstance(file_name,Path):
        file_name = Path(file_name)
    file_stem = file_name.stem
    file = Path(SUMMARY_DIR,f"{file_stem}.json")
    return file.exists()

def check_diz_dir(file_name:Path):
    if not isinstance(file_name,Path):
        file_name = Path(file_name)
    file_stem = file_name.stem
    file = Path(DIARIZE_DIR,f"{file_stem}.json")
    return file.exists()

def check_segment_dir(file_name:Path):
    if not isinstance(file_name,Path):
        file_name = Path(file_name)
    file_stem = file_name.stem
    file = Path(SEGMENT_DIR,f"{file_stem}.json")
    return file.exists()

def check_digest_dir(file_name:Path):
    if not isinstance(file_name,Path):
        file_name = Path(file_name)
    file_stem = file_name.stem
    file = Path(DIGEST_DIR,f"{file_stem}.json")
    return file.exists()

from google.cloud import storage

# Assuming your service account credentials are set up properly
client = storage.Client.from_service_account_json(Path(COMMON_DIR,Path(f'sa_gcs.json')))
# def save_summary_to_gcs(source_file:Path, file_name: str, bucket_name: str=BUCKET_NAME):
#     """Saves a dictionary as JSON to GCS bucket.

#     Args:
#         doc: The dictionary to save.
#         file_name: The name of the file to save.
#         bucket_name: The name of the GCS bucket.
#     """

#     bucket = client.bucket(bucket_name)
#     blob = bucket.blob(f'data/transcripts/summary/{file_name}')

#     # Upload the dictionary as a JSON string
#     # blob.upload_from_string(json.dumps(doc))
#     blob.upload_from_filename(source_file.as_posix())
#     # Verify if the blob exists
#     exists = blob.exists()
#     print(f"Upload successful: {exists}")
#     return exists


def get_gcs_path_for_file(file_path:Path):pass 


def check_question_dir(file_name:Path):
    if not isinstance(file_name,Path):
        file_name = Path(file_name)
    file_stem = file_name.stem
    file = Path(QUESTIONS_DIR,f"{file_stem}.json")
    return file.exists()

## transcript text
from gpt_app.common.utils_dir import client as gcs_client

def load_transcript_doc(filename:Path,gcs=False)->str:

    if not isinstance(filename,Path):
        filename=Path(filename)
    if gcs:
        blob_path = _make_file_path(TS_DIR,filename,format='json',local=False)

  
        bucket = gcs_client.bucket(BUCKET_NAME)
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            blob = bucket.blob(blob_path)
            exists = blob.exists()
            print(f"Exists: {exists}")
            blob.download_to_filename(temp_file.name)
            with open(temp_file.name,'r') as fr:
                transcript_dict = json.load(fr)
                return transcript_dict['text']
    else:
            
        path = Path(TS_DIR,f"{filename.stem}.json")
        with open(path,'r') as fr:
            transcript_dict = json.load(fr)
        return transcript_dict['text']

def load_question_doc(filename:Path)->str:
    if not isinstance(filename,Path):
        filename=Path(filename)
    path = Path(QUESTIONS_DIR,f"{filename.stem}.json")
    with open(path,'r') as fr:
        questions = json.load(fr)
    return questions

def update_transcript_doc(filename:Path,text:str)->str:
    if not isinstance(filename,Path):
        filename=Path(filename)

    print("file updating ")
    
    if not check_ts_dir(file_name=filename):
        raise Exception("No File by that name in transcripts: %s",filename.stem)
    
    path = Path(TS_DIR,f"{filename.stem}.json")
    with open(path,'r') as fr:
        transcript_dict = json.load(fr)
    if len(text) < (0.8* len(transcript_dict['text'])):
        raise Exception("Updated Text too less, please check!")
    print(text)
    transcript_dict['text']=text

    print(path.__str__())
    print(transcript_dict['text'])
    with open(path,'w') as fw:
        json.dump(transcript_dict,fw)
        return filename

def save_summary_doc(doc_summary_dict, filename):
    if not isinstance(filename,Path):
        filename = Path(filename)
    output_file = Path(SUMMARY_DIR,f'{filename.stem}.json')
    with open(output_file,'w') as fw:
        json.dump(doc_summary_dict,fw)
    return output_file

def save_digest_doc(digest_dict, filename):
    if not isinstance(filename,Path):
        filename = Path(filename)
    output_file = Path(DIGEST_DIR,f'{filename.stem}.json')
    with open(output_file,'w') as fw:
        json.dump(digest_dict,fw)
    return output_file

def save_diarize_doc(doc_summary_dict, filename):
    if not isinstance(filename,Path):
        filename = Path(filename)
    output_file = Path(DIARIZE_DIR,f'{filename.stem}.json')
    with open(output_file,'w') as fw:
        json.dump(doc_summary_dict,fw)
    return output_file

def save_segment_doc(doc_summary_dict, filename):
    if not isinstance(filename,Path):
        filename = Path(filename)
    output_file = Path(SEGMENT_DIR,f'{filename.stem}.json')
    print("saving output file to: ",output_file)
    with open(output_file,'w') as fw:
        json.dump(doc_summary_dict,fw)
    print("SAVED")
    return output_file

def save_questions_doc(questions, filename):
    if not isinstance(filename,Path):
        filename = Path(filename)
    output_file = Path(QUESTIONS_DIR,f'{filename.stem}.json')
    print("saving output file to: ",output_file)
    with open(output_file,'w') as fw:
        json.dump(questions,fw)
    print("SAVED")
    return output_file

def _save_embedded_doc(embedded_doc_dict, filename):
    if not isinstance(filename,Path):
        filename = Path(filename)
    output_file = Path(EMBEDDING_DIR,f'{filename.stem}.json')
    with open(output_file,'w') as fw:
        json.dump(embedded_doc_dict,fw)
    return output_file


## mini-corpus-chunks-into-embedding


def _load_chunks_summary_doc(file_name,gcs=False)->dict:
    print("openingchunks summary")
    if not isinstance(file_name,Path):
        file_name = Path(file_name)
    if gcs:
        blob_path = _make_file_path(SUMMARY_DIR,file_name,format='json',local=False)

  
        bucket = gcs_client.bucket(BUCKET_NAME)
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            blob = bucket.blob(blob_path)
            exists = blob.exists()
            print(blob_path)
            print(f"Exists: {exists}")
            blob.download_to_filename(Path(SUMMARY_DIR,file_name))
            print(json.load( open(Path(SUMMARY_DIR,file_name),'r')))
   
            with open(Path(SUMMARY_DIR,file_name),'r') as fr:
                summary_doc = json.load(fr)
                print(summary_doc,"summary doc")
                return summary_doc
    else:
        file_path = Path(SUMMARY_DIR,f'{file_name.stem}.json')
        with open(file_path, 'r') as fr:
            return json.load(fr)
    
def _load_chunks_diarized_doc(file_name)->dict:
    if not isinstance(file_name,Path):
        file_name = Path(file_name)
    file_path = Path(DIARIZE_DIR,f'{file_name.stem}.json')
    with open(file_path, 'r') as fr:
        text =  json.load(fr)
    full_text= []
    for i in text:
        full_text.append(text[i]['diarize'])
    return ' '.join(full_text)


def _load_chunks_segment_doc(file_name)->dict:
    try:
        if not isinstance(file_name,Path):
            file_name = Path(file_name)
        file_path = Path(SEGMENT_DIR,f'{file_name.stem}.json')
        print("opening FILE",file_path )
        with open(file_path, 'r') as fr:
            text =  json.load(fr)
        return text
    except Exception as e:
        raise MissingStageFile("Error: %s",e.__str__())
    
def _load_digest_doc(file_name)->dict:
    if not isinstance(file_name,Path):
        file_name = Path(file_name)
    file_path = Path(DIGEST_DIR,f'{file_name.stem}.json')
    with open(file_path, 'r') as fr:
        text =  json.load(fr)
    
    return text
def list_embedding_dir():
    return [str(item.stem) for item in EMBEDDING_DIR.iterdir()]
## audio-text-processing

from  gpt_app.common.dirs import *


def save_transcript_srt(transcribed_srt,
                        file_name,
                        dir=PROCESSED_DIR):
    fpath = Path(dir,f'{file_name}.srt')
    print("saving subtitle  file to...", fpath)
    with open(fpath, 'w') as f:
        f.write(transcribed_srt)
    return True


def save_transcript_text_json(transcribed_text:openai.types.audio.transcription.Transcription, 
                      file_name,dir=TS_DIR,
                      added_by=None):
    if not transcribed_text:
        raise ValueError("Missing arguments")
    fpath = Path(dir,f'{file_name.stem}.json')
    print("saving json file to...", fpath)
    ts_dict = transcribed_text.__dict__
    ts_dict['added_by'] = added_by
    with open(fpath, 'w') as f:
        json.dump(ts_dict,f)
    return fpath



    
if __name__ == '__main__':
    def test_check_ts_dir():
        f = 'Avanti_Feeds_Ltd_Q4_FY2023-24_Earnings_Conference_Call.mp4'
        return check_ts_dir(f)
    
    def test_gcs_upload():
        # f = 'Morepen_Laboratories_Ltd_Q4_FY2023-24_Earnings_Conference_Call.json'
        f = 'Avanti_Feeds_Ltd_Q4_FY2023-24_Earnings_Conference_Call.json'
        chunk_doc = _load_chunks_summary_doc(f)
        return _make_file_path(SUMMARY_DIR,f,local=False)
        # return save_summary_to_gcs(file_name=f,source_file=Path(SUMMARY_DIR,f))

    def test_gcs_read():
        fs = 'Bharti_Airtel_Ltd_Q4_FY2023-24_Earnings_Conference_Call.json'
        return _load_chunks_summary_doc(fs,gcs=True)
    

    # print(test_check_ts_dir())
    # print(test_gcs_upload())
    print(test_gcs_read())