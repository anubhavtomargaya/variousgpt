


import tempfile
from pydub import AudioSegment
from google.cloud import storage
from pathlib import Path
from dirs import CHOP_DIR, PROCESSED_DIR, TS_DIR, YOUTUBE_DIR
# from db_supabase import check_ts_exist,insert_transcript_entry,update_transcript_entry
import json

from utils import upload_blob_to_gcs_bucket_by_filename 
from utils import get_openai_client
from transcribe_chunks import transcribe_segment_memory
client = get_openai_client()

BUCKET_NAME = 'gpt-app-data'
SRC_BUCKET = 'youtube-bucket-audio'
gcs_client = storage.Client()
# gcs_client = storage.Client.from_service_account_json(Path(f'sa_gcs.json'))

def save_transcript_text_json(transcribed_text, 
                            file_name,
                            dir=TS_DIR):
    if not transcribed_text:
        raise ValueError("Missing arguments")
    fpath = Path(dir,f'{Path(file_name).name.split(".")[0]}.json')
    print("saving json file to...", fpath)
    with open(fpath, 'w') as f:
        json.dump(transcribed_text,f)
    return True

def _make_file_path(direcotry:Path,
                    file_name:Path,
                    format:str=None,
                    local=True):
    if not format:
        format = Path(file_name).as_posix().split('.')[-1]
    file_ = f"{Path(file_name).stem}.{format}"
    if local:
        return Path(direcotry,file_)
    else:
        parts = direcotry.parts
        if not "data" in parts:
            raise ValueError("DATA DIR not found in path")
        
        data_index = parts.index("data")
        after_data = "/".join(parts[data_index:])

        return f"{after_data}/{file_}"
    



def open_audio_as_segment(audio_file,dir=YOUTUBE_DIR,
                          format=None,
                          local=True):
    """ download file and open as segmnt """
    try:
        if local:
            file_path = Path(dir,audio_file)
            print(file_path)
        # audio = AudioSegment.from_file(file_path)
        else:
            print("getting from bucket", SRC_BUCKET)
            bucket = gcs_client.bucket(SRC_BUCKET)

      
            audio_file_gcs = _make_file_path(dir,
                                            audio_file,
                                            format=format,
                                            local=False)
        
            print('aduo file path', audio_file_gcs)
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                blob = bucket.blob(audio_file_gcs)
                exists = blob.exists()
                print(f"Exists: {exists}")
                blob.download_to_filename(temp_file.name)
                file_path = temp_file.name
                print('fpath',file_path)
        audio = AudioSegment.from_file(file_path)

        return audio
    except FileNotFoundError as e:
        print(f"Error: Audio file '{audio_file}' not found.")
        raise e
    
def chop_audio(audio_file:Path,audio_segment:AudioSegment, n_minutes=10, chop_dir=Path('/tmp'), source_dir=PROCESSED_DIR, format='ogg'):
    """Chops the given file in pieces of n minutes, yields each chunk."""
    # audio = open_audio_as_segment(audio_file, dir=source_dir,local=)
    total_duration_milliseconds = len(audio_segment)
    total_duration_seconds = total_duration_milliseconds / 1000
    print(f"Total audio length: {total_duration_seconds}")
    
    segment_length = n_minutes * 60 * 1000
    start_time = 0
    segment_num = 1
    
    print("starting chop")
    while start_time < total_duration_milliseconds:
        end_time = min(start_time + segment_length, total_duration_milliseconds)
        segment = audio_segment[start_time:end_time]
        # output_name = f"{audio_file.stem}_{segment_num}.{format}"
        output_name = f"{Path(audio_file).stem}_{segment_num}.{format}"
        segment_path = Path(chop_dir, output_name)
        segment.export(segment_path, format=format)
        
        yield segment_path
        # segment.export(Path(chop_dir, output_name), format=format)
        # yield segment
        
        start_time += segment_length
        segment_num += 1
    
    print(f"Audio file chopped into {segment_num - 1} segments successfully!")

def service_audio_to_gcs_transcript(f):
    """ opens the file from bucket 

    Args:
        f (_type_): file name in youtube dir

    Returns:
        _type_: _description_
    """
    audio = open_audio_as_segment(f,local=False)
    ip_fmt = Path(f).name.split('.')[-1]
    generator = chop_audio(f,audio,n_minutes=2,format=f.split('.')[-1])
    print('gen')
    print(generator)
    prompt = ''
    transcription = {'text':''}
    for chunk in generator:
        trx = transcribe_segment_memory(client,chunk,prompt,ip_fmt=ip_fmt)
        text = trx.text
        print('tdx',trx)
        print('txt',text)
        prompt = text
        transcription['text'] += text
        # break


    fpath = save_transcript_text_json(transcription,
                                        f,dir=TS_DIR)
    
    if fpath:

        print('id', "file processsed as ts: ", f)
        return upload_blob_to_gcs_bucket_by_filename(gcs_client,Path(f).stem.split('.')[0],TS_DIR,format='json')
        


if __name__=='__main__':
    f= 'FIRST_LOOK_2025_Corvette_ZR1_–_1064hp_Turbos_&_215mph!.webm'
    def test_open_gcs_audio():
        return open_audio_as_segment(f,local=False)
    
    def test_yeild_chop():
        audio = open_audio_as_segment(f,local=False)
        generator = chop_audio(f,audio,n_minutes=2,format=f.split('.')[-1])
        print('gen')
        print(generator)

    def test_process_generated_chop():
        audio = open_audio_as_segment(f,local=False)
        generator = chop_audio(f,audio,n_minutes=2,format=f.split('.')[-1])
        print('gen')
        print(generator)
        for chunk_path in generator:
            print(chunk_path)
            print('chunk')



    def test_transcribing_chunks():
        audio = open_audio_as_segment(f,local=False)
        ip_fmt = Path(f).name.split('.')[-1]
        generator = chop_audio(f,audio,n_minutes=2,format=f.split('.')[-1])
        print('gen')
        print(generator)
        prompt = ''
        result = []
        for chunk in generator:
            trx = transcribe_segment_memory(client,chunk,prompt,ip_fmt=ip_fmt)
            text = trx.text
            print('tdx',trx)
            print('txt',text)
            prompt = text
            result.append(text)
        return result

       
    def test_saving_service():
        return service_audio_to_gcs_transcript(f)
    




    # print(test_open_gcs_audio())
    # print(test_yeild_chop())
    # print(test_process_generated_chop())
    # print(test_transcribing_chunks())
    print(test_saving_service())