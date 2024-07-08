## get link from youtube, save audio in data dir 

from pathlib import Path
from pytube import YouTube
from gpt_app.common.dirs import YOUTUBE_DIR,BUCKET_NAME
from gpt_app.common.utils_dir import _make_file_path, check_ts_dir,client
from gpt_app.common.session_manager import get_user_email
import json 

class YoutubeMetadata:
    def __init__(self, 
                 title,
                 file_path,
                 thumbnail_url,
                 description,
                 length_minutes,
                 id,) -> None:
        self.id=id
        self.title = title
        self.file_path = file_path
        self.thumbnail_url = thumbnail_url
        self.description = description
        self.length_minutes = length_minutes
        self.whisper_approx_cost =round( 1.1* 0.006 * self.length_minutes ,4)

YOUTUBE_META_FILE = Path(YOUTUBE_DIR,'index.json')

def check_yt_exists():
    with open(YOUTUBE_META_FILE, 'r+') as f:
        try:
            existing_data = json.load(f)
        except json.JSONDecodeError:
            existing_data = []
        
def open_youtube_index_meta():
     with open(YOUTUBE_META_FILE, 'r+') as f:
        try:
            existing_data = json.load(f)
        except json.JSONDecodeError:
            existing_data = []
        return existing_data

def update_youtube_index_meta(meta:YoutubeMetadata):
    with open(YOUTUBE_META_FILE, 'r+') as f:
        try:
            existing_data = json.load(f)
        except json.JSONDecodeError:
            existing_data = []
    existing_data.append(meta.__dict__)

    with open(YOUTUBE_META_FILE, 'w+') as f:
        json.dump(existing_data,f,indent=4)
    return True

def get_file_name(title):
    return f"{str(title).replace(' ','_')}.mp3"

def generate_yt_file_meta(yt):pass 

def download_local():pass

def download_to_gcs(stream,client):
    print("Starting gcs...")
     
    filename = stream.default_filename.replace(' ','_')

    bucket = client.bucket(BUCKET_NAME)
    destination_blob_name = _make_file_path(YOUTUBE_DIR,filename,local=False)
    print("gcs name,",destination_blob_name)
    blob = bucket.blob(destination_blob_name)
    if blob.exists():
        print("blob exists")
        return destination_blob_name
    else:
        # Download audio stream to a byte stream
        video_data = stream.download()

        # Upload audio data to the GCS blob
        upload = blob.upload_from_string(video_data)
        print("gcs up,",upload)
        return destination_blob_name

from gpt_app.common.supabase_handler import check_yt_exist,insert_yt_entry
def download_youtube_audio(url,
                            dir = YOUTUBE_DIR,
                            local=False):
    
    """Downloads the audio from a YouTube video and saves it as an MP3 file using pytube.

    Args:
        url (str): The URL of the YouTube video.
        output_filename (str, optional): The desired filename for the downloaded audio. Defaults to "audio.mp3".

    Raises:
        Exception: If there's an error downloading the audio.
    """

    try:
        #TODO: check if url exists downloaded 
        yt = YouTube(url)
        yt_meta =  check_yt_exist(url)
        if yt_meta:
            return yt_meta[0]
        else:
            pass 
        print("starting stream check")
        print("made yt:",)
        stream = yt.streams.filter(only_audio=True, ).order_by('abr').asc().first() # select stream by lowest bit rate 
        print("starting download....", stream.__dict__) 
        
        if local:
            output_file = stream.download(output_path=dir,
                                        filename=stream.default_filename.replace(' ','_'))
        else:
            output_file = download_to_gcs(stream,client)
            if not Path(YOUTUBE_DIR,stream.default_filename.replace(' ','_')).exists():
                output_file = stream.download(output_path=dir,
                                        filename=stream.default_filename.replace(' ','_')) #tmp fix to save to local as well
            else:
                print("local exists VIDEO")
                output_file = Path(YOUTUBE_DIR,stream.default_filename.replace(' ','_'))
        m = YoutubeMetadata(id=url,title=yt.title,
                               file_path=Path(output_file).name,
                               thumbnail_url=yt.thumbnail_url,
                               description=yt.description,
                               length_minutes= round(yt.length / 60, 2),
                               )
        insert_yt_entry(meta=m.__dict__,link=f"{url}",added_by=get_user_email())
       
        w = update_youtube_index_meta(m)
        print("meta updated ", w, m.__dict__)    

        print(f'Downloaded audio from "{yt.title}" to "{output_file}"')
        return m

    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == '__main__':
    youtube_url = 'https://youtu.be/qsnXSd4iRYI?si=tck7vSlH4sXMhvfp'

    download_youtube_audio(youtube_url,local=False)
