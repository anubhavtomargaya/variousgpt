from pathlib import Path
from openai import OpenAI
from pydub import AudioSegment

from process_audio import preprocess_audio_for_transcription
DATA_DIR = Path(Path(__file__).parent.resolve(), 'data')
PROCESSED_DIR = Path(DATA_DIR, 'processed')
CHOP_DIR = Path(PROCESSED_DIR, 'chopped')

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

def transcribe_audio(client:OpenAI,audio_file_path):

    with open(audio_file_path, 'rb') as audio_file:
        transcription = client.audio.transcriptions.create( model= "whisper-1",file=audio_file)
    return transcription




def transcribe_audio_as_subtitles(client,audio_file_path):
    with open(audio_file_path, 'rb') as af:
        transcription = client.audio.transcriptions.create( model= "whisper-1", file=af,
                                                            response_format="srt",
                                                            )
    return transcription

def transcribe_audio_as_default(client,audio_file_path):
    with open(audio_file_path, 'rb') as af:
        transcription = client.audio.transcriptions.create( model= "whisper-1", file=af,
                                                            response_format="jsono",
                                                            )
    return transcription

def transcribe_audio_with_ts(client,audio_file_path):
    with open(audio_file_path, 'rb') as af:
        transcription = client.audio.transcriptions.create( model= "whisper-1", file=af,
                                                            response_format="verbose_json",
                                                            timestamp_granularities=["segment"]
                                                            )
    return transcription # not working as expected, fall back to creating srt or normal text.

def write_trx_as_subtitles(transcribed_srt, file_name,dir=PROCESSED_DIR):
    with open(Path(dir,f'{file_name}.srt'), 'w') as f:
        f.write(transcribed_srt)
    return True


if __name__ =='__main__':
    from openai import OpenAI
    from chatgpt.utils import get_openai_client
    client = get_openai_client()
    client.timeout=50
    f = 'earning_call_morepen.ogg'
    def test_pre_process_to_ogg():

        return convert_audio_to_ogg(f)

    def test_open_and_cost():
        audio = open_audio_as_segment(f)
        return get_trx_cost(audio=audio)

    def test_chop():
        f = '/Users/anubhavtomar/2023_projects/chatgpt/chatgpt/data/processed/earning_call_morepen.ogg'
        return chop_audio(Path(f))
    
    # print(test_pre_process_to_ogg()) 
    print(test_chop())
    # print(test_open_and_cost())
    
    