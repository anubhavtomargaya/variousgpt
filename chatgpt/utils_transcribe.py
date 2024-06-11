from pathlib import Path
import json
from datetime import datetime,timedelta
import openai

from enums import tsFormats
from dirs import *


def write_trx_as_subtitles(transcribed_srt,
                            file_name,
                            dir=PROCESSED_DIR):
    fpath = Path(dir,f'{file_name}.srt')
    print("saving subtitle  file to...", fpath)
    with open(fpath, 'w') as f:
        f.write(transcribed_srt)
    return True


def write_trx_as_json(transcribed_text:openai.types.audio.transcription.Transcription, 
                      file_name,dir=PROCESSED_DIR):
    if not transcribed_text:
        raise ValueError("Missing arguments")
    fpath = Path(dir,f'{file_name}.json')
    print("saving json file to...", fpath)
    with open(fpath, 'w') as f:
        json.dump(transcribed_text.__dict__,f)
    return True


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
        print("total cost $", round(0.006*total_time.seconds),2)
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

   

    # print(test_pre_process_to_ogg()) 
    # print(test_open_and_cost())
    # print(test_open_and_cost_chopped())


    # print(test_chop())
    
    