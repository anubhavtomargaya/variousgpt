from urllib.parse import unquote
from flask import Flask, render_template, jsonify, request
import yt_dlp
import os
import logging
from gcs_utils import upload_blob, blob_exists, get_blob_url
import re

FFMPEG_LOCATION = '/opt/homebrew/bin/ffmpeg'
app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

# Sample media items (mimicking database)
media_items = [
    {"id": 1, "type": "youtube", "title": "Relaxing Jazz Music", "url": "https://www.youtube.com/watch?v=neV3EPgvZ3g"},
    {"id": 2, "type": "podcast", "title": "TED Radio Hour", "url": "https://www.npr.org/podcasts/510298/ted-radio-hour"},
    {"id": 3, "type": "audio", "title": "Sample Audio", "url": "https://file-examples-com.github.io/uploads/2017/11/file_example_MP3_700KB.mp3"},
]

def extract_video_id(url):
    # Regular expressions to match various YouTube URL formats
    patterns = [
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=([^&]+)',  # Matches full YouTube URLs
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/embed\/([^?&]+)',   # Matches embed YouTube URLs
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/v\/([^?&]+)',       # Matches /v/ YouTube URLs
        r'(?:https?:\/\/)?(?:www\.)?youtu\.be\/([^?&]+)',             # Matches shortened youtu.be URLs
        r'^([a-zA-Z0-9_-]{11})$'                                      # Matches raw YouTube video IDs (11 characters)
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None

@app.route('/')
def index():
    return render_template('index.html', media_items=media_items)

@app.route('/<path:youtube_link>', methods=['GET'])
def process_youtube(youtube_link):
    print(youtube_link)
    decoded_link = unquote(youtube_link)
    
    # Extract video ID
    video_id = youtube_link
    if not video_id:
        return render_template('import.html', error="Invalid YouTube link or ID"), 400
    
    # Process the video (download, upload, etc.) and generate the URL
    # Here, you would add your processing logic as before
    
    # For demonstration, return the video ID and the decoded URL
    # return render_template('import.html', video_id=video_id, url=decoded_link, success="Processing successful")

    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'ffmpeg_location': FFMPEG_LOCATION,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': '/tmp/%(id)s.%(ext)s',
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
            filename = f"{video_id}.mp3"
            
            if not blob_exists(filename):
                local_file = f"/tmp/{filename}"
                ydl.download([f"https://www.youtube.com/watch?v={video_id}"])
                audio_url = upload_blob(local_file, filename)
                os.remove(local_file)  # Clean up the local file
            else:
                audio_url = get_blob_url(filename)
        
        processing_meta = {
            "title": info.get('title', 'Unknown'),
            "duration": info.get('duration', 'Unknown'),
            "upload_date": info.get('upload_date', 'Unknown'),
        }
        
        return render_template('import.html', success=True, audio_url=audio_url, meta=processing_meta)
    
    except Exception as e:
        app.logger.error(f"Error processing YouTube video: {str(e)}")
        return render_template('import.html', error=f"Could not process YouTube video: {str(e)}"), 500

@app.route('/play/<int:media_id>')
def play_media(media_id):
    media = next((item for item in media_items if item["id"] == media_id), None)
    if not media:
        return jsonify({"error": "Media not found"}), 404
    
    if media["type"] == "youtube":
        video_id = extract_video_id(media["url"])
        if video_id:
            filename = f"{video_id}.mp3"
            if blob_exists(filename):
                audio_url = get_blob_url(filename)
                return jsonify({"url": audio_url, "title": media["title"], "type": "youtube"})
    
    return jsonify({"url": media["url"], "title": media["title"], "type": media["type"]})

if __name__ == '__main__':
    app.run(debug=True)