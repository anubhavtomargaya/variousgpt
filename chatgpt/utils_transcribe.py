
from datetime import datetime
import openai
from enums import tsFormats
import io
def transcribe_segment_memory(segment,
                              prompt='',
                              fmt=None):
    audio_buffer = io.BytesIO()
    segment.export(audio_buffer)  # Adjust format as needed
    audio_buffer.seek(0)  # Reset buffer position to the beginning
    print("calling openai whisper started...")
    st = datetime.utcnow()
    transcription = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_buffer,
        response_format='json',
        prompt=prompt
    )
    print("calling openai end.")
    et = datetime.utcnow()
    total_time = et - st
    print("total time ", total_time.seconds, 'seconds')
    print("total cost $", round(0.006 * total_time.seconds, 2))
    
    return transcription

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
    
    