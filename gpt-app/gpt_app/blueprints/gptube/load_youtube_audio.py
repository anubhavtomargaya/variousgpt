## get link from youtube, save audio in data dir 

from pathlib import Path
from pytube import YouTube
from gpt_app.common.dirs import YOUTUBE_DIR
import json 

class YoutubeMetadata:
    def __init__(self, 
                 title,
                 file_path,
                 thumbnail_url,
                 description,
                 length_minutes) -> None:
        
        self.title = title
        self.file_path = file_path
        self.thumbnail_url = thumbnail_url
        self.description = description
        self.length_minutes = length_minutes

YOUTUBE_META_FILE = Path(YOUTUBE_DIR,'index.json')
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
        yt = YouTube(url)

        print("starting stream check")
        print("made yt:",yt.__dict__)
        stream = yt.streams.filter(only_audio=True, ).order_by('abr').asc().first() # select stream by lowest bit rate 

        print("starting download....", stream.__dict__)
        output_file = stream.download(output_path=dir,
                                      filename=stream.default_filename.replace(' ','_'))
       

        meta = YoutubeMetadata(title=yt.title,
                               file_path=output_file,
                               thumbnail_url=yt.thumbnail_url,
                               description=yt.description,
                               length_minutes= round(yt.length / 60, 2) )
       
        w = update_youtube_index_meta(meta)
        print("meta updated ", w, meta.__dict__)    

        print(f'Downloaded audio from "{yt.title}" to "{output_file}"')
        return meta

    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == '__main__':
    youtube_url = 'https://youtu.be/qsnXSd4iRYI?si=tck7vSlH4sXMhvfp'

    download_youtube_audio(youtube_url)
