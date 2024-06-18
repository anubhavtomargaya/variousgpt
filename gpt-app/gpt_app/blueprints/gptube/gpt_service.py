from datetime import datetime
from  gpt_app.common.enums import tsFormats
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
        print("total processing time ", total_time.seconds, 'seconds')
        print("total cost $", round(0.006*total_time.seconds),2)
    return transcription