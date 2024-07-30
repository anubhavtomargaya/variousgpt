  

import io
from datetime import datetime

def transcribe_segment_memory(client,
                              segment_file,
                              prompt='',
                              ip_fmt='mp4',
                              fmt=None):
    # audio_buffer = io.BytesIO()
    # segment.export(audio_buffer,  format=ip_fmt)  # Adjust format as needed
    # audio_buffer.seek(0)  # Reset buffer position to the beginning
    print("calling openai whisper started...")
    st = datetime.utcnow()
    # print(audio_buffer)
    print(ip_fmt)
    transcription = client.audio.transcriptions.create(
        model="whisper-1",
        file=segment_file,
        response_format='json',
        prompt=prompt
    )
    print("calling openai end.")
    et = datetime.utcnow()
    total_time = et - st
    print("total time ", total_time.seconds, 'seconds')
    print("total cost $", round(0.006 * total_time.seconds, 2))
    
    return transcription