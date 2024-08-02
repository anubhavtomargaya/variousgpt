from flask import Request, jsonify
from google.cloud import storage
from pathlib import Path
from pytube import YouTube
import json 

from db_supabase import   check_yt_exist,insert_yt_entry
from dirs import YOUTUBE_DIR    
from pytube_fix import imp                                                                                         

#utils.py
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

#consts.py
APP_BUCKET = 'gpt-app-data'
BUCKET_NAME = 'youtube-bucket-audio'
# gcs_client = storage.Client()
gcs_client = storage.Client.from_service_account_json(Path(f'sa_gcs.json'))

## get link from youtube, save audio in data dir 


TMP_DIR = Path('/tmp')

class YoutubeMetadata:
    def __init__(self, 
                 title,
                 thumbnail_url,
                 description,
                 length_minutes,
                 id,
                 file_path=None,
                 ) -> None:
        self.id=id
        self.title = title
        self.file_path = file_path
        self.thumbnail_url = thumbnail_url
        self.description = description
        self.length_minutes = length_minutes
        self.whisper_approx_cost =round( 1.1* 0.006 * self.length_minutes ,4)

def get_youtube_object(url):
    return YouTube(url)

def get_youtube_stream(yt:YouTube):
    try:

        return yt.streams.filter(only_audio=True, ).order_by('abr').asc().first() # select stream by lowest bit rate 
    except Exception as e:
        raise Exception("unable to get stream :")
    
def service_download_youtube_audio(url,
                            dir = YOUTUBE_DIR,
                            user='worker'):
    
    """Downloads the audio from a YouTube video and saves it as an MP3 file using pytube.

    Args:
        url (str): The URL of the YouTube video.
        output_filename (str, optional): The desired filename for the downloaded audio. Defaults to "audio.mp3".

    Raises:
        Exception: If there's an error downloading the audio.
    """

    try:
        #TODO: check if url exists downloaded 
        yt_meta = check_yt_exist(url)
        if yt_meta:
            return yt_meta[0]
        
        yt = get_youtube_object(url)
        yt_meta = YoutubeMetadata(id=url,title=yt.title,
                                thumbnail_url=yt.thumbnail_url,
                                description=yt.description,
                                length_minutes= round(yt.length / 60, 2),
                                )
        
        
        print("starting stream check")
        print("made yt:",)
        print(yt)
        stream = get_youtube_stream(yt)

        print("starting download....", stream.__dict__) 
        
        #download stream locally
        link_file_name = stream.default_filename.replace(' ','_')
        output_file = stream.download(output_path=TMP_DIR,
                                    filename=link_file_name) 
        print('ouput file',output_file)
        bucket = gcs_client.bucket(BUCKET_NAME)
        destination_blob_name = _make_file_path(YOUTUBE_DIR,link_file_name,local=False)
        print("gcs name,",destination_blob_name)
        blob = bucket.blob(destination_blob_name)
        print(blob)
        yt_meta.file_path=Path(output_file).name
        if not blob.exists():
            print("blob  no exists")
            # Download audio stream to a byte stream
            with open(output_file, 'rb') as file_data:
                blob.upload_from_file(file_data)
            print("File uploaded")
    
           
            print(f'Downloaded audio from "{yt.title}" to "{output_file}"')
            insert_yt_entry(meta=yt_meta.__dict__,link=f"{url}",added_by=user)
            return {'meta': yt_meta.__dict__}
        else:
            return yt_meta
  

    except Exception as e:
        print(f"Unexpected error: {e}")
        return False
    
def download_audio_youtube(event, context=None):
    if not isinstance(event,dict):
        request_json = event.get_json()
        link = request_json['url']
        user = request_json['user']
    else:
        link = request_json['url']
        user = request_json['user']
        file_path = event['name']
        file_name = Path(file_path).name
    # bucket_name = event['bucket']
    # print(f"Processing file: {file_name} in sbucket: {bucket_name}")
    return service_download_youtube_audio(url=link)

if __name__ == '__main__':
    url = 'https://www.youtube.com/watch?v=8ybNkgC0eHY'
    def test_service():
        return service_download_youtube_audio(url)

    print(test_service())