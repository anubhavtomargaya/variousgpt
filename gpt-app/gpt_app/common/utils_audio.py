
import tempfile
from pydub import AudioSegment
from gpt_app.common.utils_openai import get_trx_cost
from gpt_app.common.utils_dir import _make_file_path
from gpt_app.common.dirs import *


import subprocess

def preprocess_audio_for_transcription(input_file, output_file,
                                       format='ogg'):
  """
  Re-encodes audio to Opus codec optimized for transcription.

  Args:
      input_file (str): Path to the input audio file.
      output_file (str): Path to save the re-encoded audio file.

  Returns:
      bool: True if successful, False otherwise.
  """
  command = [
      "ffmpeg",
      "-i", input_file,
      "-vn",  # Disable video processing
      "-map_metadata", "-1",  # Prevent copying metadata
      "-ac", "1",  # Mono audio
      "-c:a", "libopus",  # Opus codec
      "-b:a", "12k",  # 12kbps bitrate (adjust as needed)
      "-application", "voip",  # Optimize for voice
      output_file,
  ]

  try:
    subprocess.run(command, check=True)
    return True
  except subprocess.CalledProcessError:
    print("Error: ffmpeg failed to process audio.")
    return False

from gpt_app.common.utils_dir import client as gcs_client


def convert_audio_to_ogg(file_name,
                         source_dir=DATA_DIR,
                         output_dir=PROCESSED_DIR,
                         local=True)->Path:
    mp3_file = Path(source_dir,file_name)
    output_file = Path(output_dir,f"{mp3_file.stem}.ogg" )
    if output_file.exists():
        return output_file
    success = preprocess_audio_for_transcription(mp3_file, output_file)
    if success:
        print(f"Audio re-encoded successfully to {output_file}")
        if not local:
            bucket = gcs_client.bucket(BUCKET_NAME)
            destination_blob_name = _make_file_path(PROCESSED_DIR,output_file,local=False)
            blob = bucket.blob(destination_blob_name)
            upload = blob.upload_from_filename(output_file)
            print("upload:",upload)
            print("gcs name,",destination_blob_name)
            print("gcs up,",upload)
            exists = blob.exists()
            print(f"Upload successful: {exists}")
            return output_file
            return exists
            return destination_blob_name
        else:
            
            print(output_file.stem)
            return output_file
            
    else:
        print("Re-encoding failed.")
        return False
    

def open_audio_as_segment(audio_file,dir=PROCESSED_DIR,format=None,local=True):
    try:
        if local:
            file_path = Path(dir,audio_file)
            print(file_path)
        # audio = AudioSegment.from_file(file_path)
        else:
            bucket = gcs_client.bucket(BUCKET_NAME)

      
            audio_file_gcs = _make_file_path(dir,
                                            audio_file,
                                            format=format,
                                            local=False)
    
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                blob = bucket.blob(audio_file_gcs)
                exists = blob.exists()
                print(f"Exists: {exists}")
                blob.download_to_filename(temp_file.name)
                file_path = temp_file.name
        audio = AudioSegment.from_ogg(file_path)

        return audio
    except FileNotFoundError as e:
        print(f"Error: Audio file '{audio_file}' not found.")
        raise e
    
def chop_audio(audio_file:Path, n_minutes=10,chop_dir=CHOP_DIR, source_dir=PROCESSED_DIR,format='ogg'):
    """chops the given file in pieces of n minutes, saves in 

    Args:
        audio_file (Path): full file path file name 
        n_minutes (int, optional): segment length. Defaults to 10.
        chop_dir (_type_, optional):output directory for chopped audio. Defaults to CHOP_DIR.
        format (str, optional): output format. Defaults to 'ogg'.
    """
    ## lets chop the file first 
    # also make sure the size doesnt exceed 25mb for each segment
    audio = open_audio_as_segment(audio_file,dir=source_dir)
    total_duration_milliseconds = len(audio)
    total_duration_seconds = total_duration_milliseconds / 1000

    # Print total audio length in seconds at the beginning
    print(f"Total audio length: {total_duration_seconds:.2f} seconds")

  # Get total audio duration in milliseconds
    total_duration = len(audio)
    segment_length = n_minutes * 60 * 1000
    # Iterate through the audio, creating and saving segments
    start_time = 0
    segment_num = 1
    
    print("starting chop")
    files = []
    while start_time < total_duration:
        print("chop done ", segment_num)

        # Ensure the last segment doesn't exceed the audio length
        end_time = min(start_time + segment_length, total_duration)
        segment = audio[start_time:end_time]
        print("segment cost :", get_trx_cost(segment))
        # Generate output filename with segment number
        output_name = f"{audio_file.stem}_{segment_num}.{format}"
        files.append(output_name)
        # output_name = f"{audio_file.stem}_{segment_num}.{format}"

        # Export the segment
        segment.export(Path(chop_dir,output_name), format=format)

        # Update start time for the next segment
        start_time += segment_length
        segment_num += 1

    print(f"Audio file chopped into {segment_num - 1} segments successfully!")
    return files


if __name__ == '__main__':
    from openai import OpenAI
    from pathlib import Path
    from gpt_app.common.utils_openai import get_openai_client

    wav_file = 'chatgpt/data/EarningsCall.wav'
    path_ = f'chatgpt/data/'
    file_name = 'earning_call_morepen.mp3'
    mp3_file = f'{path_}{file_name}'
    output_file = f"{path_}processed_{file_name.split('.')[0]}.ogg"
    success = preprocess_audio_for_transcription(mp3_file, output_file)
    if success:
        print(f"Audio re-encoded successfully to {output_file}")
    else:
        print("Re-encoding failed.")

    openai_client = get_openai_client()
    openai_client.timeout=50
    # f = 'earning_call_morepen.ogg'
    f = 'Raymond Ltd Q4 FY2023-24 Earnings Conference Call.mp4'
    f_chopped = 'earning_call_morepen_1.ogg'

    def test_pre_process_to_ogg():
        return convert_audio_to_ogg(f)  
    
    def test_pre_process_to_ogg_gcs():
        return convert_audio_to_ogg(f,local=False)  
    
    def test_open_and_cost():
        audio = open_audio_as_segment(f)
        return get_trx_cost(audio=audio)
    
    def test_open_and_cost_gcs():
        audio = open_audio_as_segment(f,local=False,format='ogg')
        return get_trx_cost(audio=audio)
    
     
    def test_chop():
        f = '/Users/anubhavtomar/2023_projects/chatgpt/chatgpt/data/processed/earning_call_morepen.ogg'
        return chop_audio(Path(f))
    
    def test_open_and_cost_chopped():
        audio = open_audio_as_segment(f,dir=PROCESSED_DIR)
        return get_trx_cost(audio=audio)
    
    # print(test_pre_process_to_ogg_gcs())
    print(test_open_and_cost_gcs())