from pydub import AudioSegment
from utils import get_trx_cost
from pre_process_audio import preprocess_audio_for_transcription
from dirs import *

def convert_audio_to_ogg(file_name,data_dir=DATA_DIR,
                         output_dir=PROCESSED_DIR)->Path:
    mp3_file = Path(data_dir,file_name)
    output_file = Path(output_dir,f"{mp3_file.stem}.ogg" )
    success = preprocess_audio_for_transcription(mp3_file, output_file)
    if success:
        print(f"Audio re-encoded successfully to {output_file}")
        print(output_file.stem)
        return output_file
    else:
        print("Re-encoding failed.")
        return False
    

def open_audio_as_segment(audio_file,dir=PROCESSED_DIR):
    try:
        file_path = Path(dir,audio_file)
        print(file_path)
        audio = AudioSegment.from_ogg(file_path)

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