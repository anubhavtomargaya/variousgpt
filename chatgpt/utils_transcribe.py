from pathlib import Path
from openai import OpenAI
from pydub import AudioSegment
from pre_process_audio import preprocess_audio_for_transcription

from dirs import *

def convert_audio_to_ogg(file_name,data_dir=DATA_DIR)->Path:
    mp3_file = Path(data_dir,file_name)
    output_file = Path(data_dir,'processed',f"{mp3_file.stem}.ogg" )
    success = preprocess_audio_for_transcription(mp3_file, output_file)
    if success:
        print(f"Audio re-encoded successfully to {output_file}")
        print(output_file.stem)
        return output_file
    else:
        print("Re-encoding failed.")
        return False
    
def get_trx_cost(audio:AudioSegment):
   
    total_duration_milliseconds = len(audio)
    total_duration_seconds = total_duration_milliseconds / 1000
    total_duration_minutes = round(total_duration_seconds/60,2)
    rate = 0.006 #  / minute
    return round(total_duration_minutes * rate, 2)

def open_audio_as_segment(audio_file,dir=PROCESSED_DIR):
    try:
        file_path = Path(dir,audio_file)
        print(file_path)
        audio = AudioSegment.from_ogg(file_path)
        print(audio)
        return audio
    except FileNotFoundError as e:
        print(f"Error: Audio file '{audio_file}' not found.")
        raise e
    
def chop_audio(audio_file:Path, n_minutes=10,chop_dir=CHOP_DIR, format='ogg'):
    """chops the given file in pieces of n minutes, saves in 

    Args:
        audio_file (Path): full file path file name 
        n_minutes (int, optional): segment length. Defaults to 10.
        chop_dir (_type_, optional):output directory for chopped audio. Defaults to CHOP_DIR.
        format (str, optional): output format. Defaults to 'ogg'.
    """
    ## lets chop the file first 
    # also make sure the size doesnt exceed 25mb for each segment
    audio = open_audio_as_segment(audio_file)
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
    while start_time < total_duration:
        print("chop done ", segment_num)

        # Ensure the last segment doesn't exceed the audio length
        end_time = min(start_time + segment_length, total_duration)
        segment = audio[start_time:end_time]
        print("segment cost :", get_trx_cost(segment))
        # Generate output filename with segment number
        output_name = f"{audio_file.stem}_{segment_num}.{format}"
        # output_name = f"{audio_file.stem}_{segment_num}.{format}"

        # Export the segment
        segment.export(Path(chop_dir,output_name), format=format)

        # Update start time for the next segment
        start_time += segment_length
        segment_num += 1

    print(f"Audio file chopped into {segment_num - 1} segments successfully!")
    return output_name

# def transcribe_audio(client:OpenAI,audio_file_path):

#     with open(audio_file_path, 'rb') as audio_file:
#         transcription = client.audio.transcriptions.create( model= "whisper-1",file=audio_file)
#     return transcription



def write_trx_as_subtitles(transcribed_srt,
                            file_name,
                            dir=PROCESSED_DIR):
    with open(Path(dir,f'{file_name}.srt'), 'w') as f:
        f.write(transcribed_srt)
    return True

import json
import openai
def write_trx_as_json(transcribed_text:openai.types.audio.transcription.Transcription, file_name,dir=PROCESSED_DIR):
    if not transcribed_text:
        raise ValueError("Missing arguments")
    
    with open(Path(dir,f'{file_name}.json'), 'w') as f:
        json.dump(transcribed_text.__dict__,f)
    return True

from datetime import datetime,timedelta
from enums import tsFormats
import openai

def transcribe_audio_in_format(client,audio_file_path,
                            format:tsFormats=tsFormats.JSON,
                            prompt="")->openai.types.audio.transcription.Transcription:
    with open(audio_file_path, 'rb') as af:
        print("calling open api whisper started...")
        st = datetime.utcnow()
        transcription = client.audio.transcriptions.create( model= "whisper-1", file=af,
                                                            response_format=format.value,
                                                            prompt=prompt
                                                            )
        print("calling open api end.")
        et = datetime.utcnow()
        total_time = et - st
        print("total time ", total_time.seconds, 'seconds')
        print("total tokens ", round(0.006*total_time.seconds))
    return transcription

def transcribe_audio_as_default(client,audio_file_path):
    with open(audio_file_path, 'rb') as af:
        transcription = client.audio.transcriptions.create( model= "whisper-1", file=af,
                                                            response_format="json",
                                                            )
    return transcription

# def transcribe_audio_with_ts(client,audio_file_path):
#     with open(audio_file_path, 'rb') as af:
#         transcription = client.audio.transcriptions.create( model= "whisper-1", file=af,
#                                                             response_format="verbose_json",
#                                                             timestamp_granularities=["segment"]
#                                                             )
#     return transcription # not working as expected, fall back to creating srt or normal text.


if __name__ =='__main__':
    from openai import OpenAI
    from utils import get_openai_client
    client = get_openai_client()
    client.timeout=50
    f = 'earning_call_morepen.ogg'
    f_chopped = 'earning_call_morepen_1.ogg'
    def test_pre_process_to_ogg():

        return convert_audio_to_ogg(f)

    def test_open_and_cost():
        audio = open_audio_as_segment(f)
        return get_trx_cost(audio=audio)
    
    def test_chop():
        f = '/Users/anubhavtomar/2023_projects/chatgpt/chatgpt/data/processed/earning_call_morepen.ogg'
        return chop_audio(Path(f))
    
    def test_open_and_cost_chopped():
        audio = open_audio_as_segment(f_chopped,dir=CHOP_DIR)
        return get_trx_cost(audio=audio)

    # print(test_pre_process_to_ogg()) 
    # print(test_open_and_cost())
    # print(test_open_and_cost_chopped())


    # print(test_chop())
    
    