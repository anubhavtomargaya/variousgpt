from pathlib import Path
import subprocess
from dirs import DATA_DIR, VIDEO_DIR

import os

def rename_video_with_underscores(video_filepath):
    """
    This function renames a video file by replacing spaces in the filename with underscores.

    Args:
        video_filepath (str): The path to the video file.

    Returns:
        str: The path to the renamed video file with underscores replacing spaces.
    """
    # Get the filename and extension from the filepath
    
    if not isinstance(video_filepath,Path):
       filename = Path(video_filepath) 
    else:
       filename = video_filepath


    # Replace spaces with underscores in the filename
    new_filename = filename.stem.replace(" ", "_")

    # Combine the new filename with the extension
    renamed_filepath = Path(video_filepath.parent.resolve(),f"{new_filename}.mp4" )

    # Rename the video file
    os.rename(video_filepath, renamed_filepath)

    return renamed_filepath

# # Example usage
# # video_file = "This video has spaces.mp4"
# # renamed_file = rename_video_with_underscores(video_file)

# # print(f"Video renamed to: {renamed_file}")
# def extract_audio(video_filename, directory_path=VIDEO_DIR, ):
#   """
#   Extracts audio from a video file using ffmpeg and saves it as MP3.

#   Args:
#       video_filename: The filename of the video file (e.g., "video.mp4").
#       directory_path: The directory path where the video file is located.
#       output_filename (optional): The desired filename for the extracted audio (default: "extracted_audio.mp3").

#   Returns:
#       True if extraction is successful, False otherwise.
#   """
#   # Construct the full video file path
#   video_path = Path(directory_path,video_filename)

#   # Build the ffmpeg command
#   print(video_path.__str__())
#   command = ["ffmpeg", "-i", video_path.__str__(), "-vn", "-acodec", "copy", f"{video_path.stem}.mp3"]

#   # Execute the command using subprocess
#   try:
#     subprocess.run(command, check=True)
#     return video_path
#   except subprocess.CalledProcessError:
#     print(f"Error extracting audio from {video_filename}")
#     return False
from moviepy.editor import VideoFileClip

def extract_audio(video_filepath, output_filepath="output.mp3"):
  """
  Attempts to extract audio from a video file using MoviePy.

  Args:
      video_filepath (str): The path to the video file.
      output_filepath (str, optional): The path to the output audio file. Defaults to "output.mp3".

  Returns:
      bool: True if extraction succeeded, False otherwise.
  """
  try:
    # Open the video clip
    clip = VideoFileClip(video_filepath)

    # Extract the audio
    audio = clip.audio

    # Write the audio to a file
    output_filepath = Path(DATA_DIR, f"{Path(video_filepath).stem}.mp3")
    print(output_filepath)
    r = audio.write_audiofile(output_filepath)
    return output_filepath if r else False
  except Exception as e:
    print(f"Error extracting audio: {e}")
    return False

# Example usage
# video_file = "Juan_Camilo_Avendano_and_Ankit_Gupta.mp4"
# success = extract_audio(video_file)

# if success:
#   print("Audio extracted successfully!")
# else:
  print("Audio extraction failed.")

if __name__=='__main__':
# Example usage
    def test_process_video():
        video_filename = "Juan_Camilo_Avendano_and_Ankit_Gupta.mp4"

        
        return extract_audio(video_filepath=Path(VIDEO_DIR,video_filename).__str__())
    # rename_video_with_underscores(Path(VIDEO_DIR,video_filename))  
    # ()

    print(test_process_video())