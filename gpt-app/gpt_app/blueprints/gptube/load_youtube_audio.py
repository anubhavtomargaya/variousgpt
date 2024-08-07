## get link from youtube, save audio in data dir 

from pathlib import Path
from pytube import YouTube
from gpt_app.common.dirs import YOUTUBE_BUCKET_NAME, YOUTUBE_DIR,BUCKET_NAME
from gpt_app.blueprints.gptube.helpers_gcs import upload_file_to_gcs
from gpt_app.common.utils_dir import _make_file_path, check_ts_dir,client
from gpt_app.common.session_manager import get_user_email
import json 

from pytube.innertube import _default_clients
from pytube import cipher
import re

_default_clients["ANDROID"]["context"]["client"]["clientVersion"] = "19.08.35"
_default_clients["IOS"]["context"]["client"]["clientVersion"] = "19.08.35"
_default_clients["ANDROID_EMBED"]["context"]["client"]["clientVersion"] = "19.08.35"
_default_clients["IOS_EMBED"]["context"]["client"]["clientVersion"] = "19.08.35"
_default_clients["IOS_MUSIC"]["context"]["client"]["clientVersion"] = "6.41"
_default_clients["ANDROID_MUSIC"] = _default_clients["ANDROID_CREATOR"]



def get_throttling_function_name(js: str) -> str:
    """Extract the name of the function that computes the throttling parameter.

    :param str js:
        The contents of the base.js asset file.
    :rtype: str
    :returns:
        The name of the function used to compute the throttling parameter.
    """
    function_patterns = [
        r'a\.[a-zA-Z]\s*&&\s*\([a-z]\s*=\s*a\.get\("n"\)\)\s*&&\s*'
        r'\([a-z]\s*=\s*([a-zA-Z0-9$]+)(\[\d+\])?\([a-z]\)',
        r'\([a-z]\s*=\s*([a-zA-Z0-9$]+)(\[\d+\])\([a-z]\)',
    ]
    #logger.debug('Finding throttling function name')
    for pattern in function_patterns:
        regex = re.compile(pattern)
        function_match = regex.search(js)
        if function_match:
            #logger.debug("finished regex search, matched: %s", pattern)
            if len(function_match.groups()) == 1:
                return function_match.group(1)
            idx = function_match.group(2)
            if idx:
                idx = idx.strip("[]")
                array = re.search(
                    r'var {nfunc}\s*=\s*(\[.+?\]);'.format(
                        nfunc=re.escape(function_match.group(1))),
                    js
                )
                if array:
                    array = array.group(1).strip("[]").split(",")
                    array = [x.strip() for x in array]
                    return array[int(idx)]

    raise Exception(
        caller="get_throttling_function_name", pattern="multiple"
    )

cipher.get_throttling_function_name = get_throttling_function_name
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
        upload_file_to_gcs()

        # Upload audio data to the GCS blob
        upload = blob.upload_from_string(video_data)
        print("gcs up,",upload)
        return destination_blob_name

from gpt_app.common.supabase_handler import check_yt_exist,insert_yt_entry
def download_youtube_audio(url,
                            dir = YOUTUBE_DIR):
    
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
        yt_meta = check_yt_exist(url)
        if yt_meta:
            return yt_meta[0]
        else:
            pass 
        print("starting stream check")
        print("made yt:",)
        print(yt)
        stream = yt.streams.filter(only_audio=True, ).order_by('abr').asc().first() # select stream by lowest bit rate 
        print("starting download....", stream.__dict__) 
        if not Path(YOUTUBE_DIR,stream.default_filename.replace(' ','_')).exists():
            output_file = stream.download(output_path=dir,
                                    filename=stream.default_filename.replace(' ','_')) #tmp fix to save to local as well
        else:
            print("local exists VIDEO")
            output_file = Path(YOUTUBE_DIR,stream.default_filename.replace(' ','_'))
        
        
        filename = stream.default_filename.replace(' ','_')

        bucket = client.bucket(YOUTUBE_BUCKET_NAME)
        destination_blob_name = _make_file_path(YOUTUBE_DIR,filename,local=False)
        print("gcs name,",destination_blob_name)
        blob = bucket.blob(destination_blob_name)
        print(blob)
        if blob.exists():
            print("blob exists")
            pass
        else:
            print("blob  no exists")
            # Download audio stream to a byte stream
            with open(output_file, 'rb') as file_data:
                blob.upload_from_file(file_data)
        print("File uploaded")
            # video_up  = upload_file_to_gcs(file=filename,filename=destination_blob_name)
        # output_file = download_to_gcs(stream,client)
        # print()
        m = YoutubeMetadata(id=url,title=yt.title,
                               file_path=Path(output_file).name,
                               thumbnail_url=yt.thumbnail_url,
                               description=yt.description,
                               length_minutes= round(yt.length / 60, 2),
                               )
        print(f'Downloaded audio from "{yt.title}" to "{output_file}"')
        insert_yt_entry(meta=m.__dict__,link=f"{url}",added_by=get_user_email())
        return {'meta': m.__dict__}
       
        w = update_youtube_index_meta(m)
        print("meta updated ", w, m.__dict__)    

    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

if __name__ == '__main__':
    youtube_url = 'https://youtu.be/qsnXSd4iRYI?si=tck7vSlH4sXMhvfp'
    # utl ='https://www.youtube.com/watch?v=bf7RjMUXomE'
    utl ='https://www.youtube.com/watch?v=sP1w5jXz1Mc'
    utl ='https://www.youtube.com/watch?v=kLVRnHykI8o'
    utl ='https://www.youtube.com/watch?v=lactCnL7lFM'
    # utl ='https://www.youtube.com/watch?v=QqqU88-71cQ'

    download_youtube_audio(utl)
