


from pathlib import Path

from models import AudioTranscript
from utils import get_openai_client
from utils_dir import save_transcript_text_json
from utils_transcribe import transcribe_audio_in_format
from workers.audio_transcribe.preproc import chop_audio,gcs_client

def transcribe_segment_single(segment,base_prompt):
    prompt = base_prompt
  
def transcribe_audio_in_chunks(audio_path:Path,
                                base_prompt:str,
                                source_dir = YOUTUBE_DIR,
                                output_dir=TS_DIR,
                                n_mins=10): # save text of each chunk (audio chunk)
    #TODO 
    # chops and stores in local dir
    # opensegment in chop can open from gcs
    # pass segment number from outside
    """ chop file and save chunks in chop dir. Finish transcription, concat transcripts and save in a AudioTranscript object to a json.
    ensure ogg file in full path is entered, base prompt to catch domain specific words.
        Transcribe each chunk sequentially reading from disk. 
        
    """
    print("AUDIOP ",audio_path)
    # meta = TranscriptMetadata(audio_file_name=audio_path.stem,
    #                           transcript_format=tsFormats.JSON)
    fmt = audio_path.name.split('.')[-1]
    # chunk_files =  [ open_audio_as_segment(audio_path,)]
    # chunk_files = chop_audio(audio_path,source_dir=source_dir,format=fmt,n_minutes=n_mins)
    chunk_files = chop_audio(audio_path, source_dir=source_dir, format=fmt, n_minutes=n_mins)
    # meta.num_chunks = None  # To be updated dynamically
    # start transcription of chunks, 
   
    print("starting transcription, got client")
    prompt = base_prompt
    output_prefix = ''
    id = 0
    transcript_final = AudioTranscript(text='', meta={'total_chunks': 0, 'count': 0})

    print("starting chunk processing...")
    for chunk_file in chunk_files:
        file_path = Path(CHOP_DIR, chunk_file)
        print("file path of chunk:", file_path.__str__())
        
        trx = transcribe_audio_in_format(client=client, audio_file_path=file_path, prompt=prompt)
        prompt = trx.text  # update prompt for next chunk 
        transcript_final.text += f'{trx.text} '
        transcript_final.meta['count'] += 1
        transcript_final.meta['total_chunks'] += 1
        
        # Optionally, send the partial transcript to the client here
        print(f"Processed chunk {chunk_file}, updated transcript: {transcript_final.text}")

    out_file_name = f'{output_prefix}{audio_path.stem}'
    if save_transcript_text_json(transcript_final, out_file_name, dir=output_dir):
        print(id, "file processed as ts:", file_path.stem)
        result = f'{out_file_name}.json'
    else:
        result = None

    return result
    # meta.num_chunks = len(chunk_files)
    # start transcription of chunks, 
    client = get_openai_client()
    print("starting transcriptioni, got client")
    prompt = base_prompt
    output_prefix = ''
    id = 0
    transcript_final = AudioTranscript(text='',meta={'total_chunks':len(chunk_files),
                                                     'count':0 
                                                     }
                                            )

    print("chunk files:", type(chunk_files), chunk_files)
    for chunk_file in chunk_files:
        file_path = Path(CHOP_DIR,chunk_file)
        print("file path of chunk :", file_path.__str__())
        
        trx = transcribe_audio_in_format(client=client,
                                        audio_file_path= file_path ,
                                        prompt=prompt)
        prompt = trx.text #update prompt for next chunk 
        transcript_final.text += f'{trx.text} '
        transcript_final.meta['count'] += 1
        

    out_file_name =  f'{output_prefix}{audio_path.stem}'

    if save_transcript_text_json(transcript_final,
                         out_file_name,
                         dir=output_dir):

        print(id, "file processsed as ts: ", file_path.stem)
        return f'{out_file_name}.json'
    else:
         raise Exception("Error while saving text as json")
    
def transcribe_audio_file(event, context=None):
    if not isinstance(event,dict):
        request_json = event.get_json()
        file_name = request_json['name']
    else:
        file_path = event['name']
        file_name = Path(file_path).name
        bucket_name = event['bucket']
        print(f"Processing file: {file_name} in bucket: {bucket_name}")