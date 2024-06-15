from pathlib import Path
from utils_dir import save_transcript_text_json, save_transcript_srt
from dirs import *
from utils import get_openai_client
from utils_transcribe import transcribe_audio_in_format

def transcribe_wth_lag_prompt(file_path:Path, 
                        prompt_file:Path,
                        output_dir=TS_DIR,
                        format:tsFormats=tsFormats.JSON,
                        base_prompt="",
                        output_prefix='wlp_'):
    print("starting transcription 1 :..")
    trx = transcribe_audio_in_format(client=get_openai_client(),
                                        audio_file_path= prompt_file ,
                                        prompt=base_prompt)
    print("starting transcription 2 :..")

    next_prompt = trx.text
    trx = transcribe_audio_in_format(client=get_openai_client(),
                                        audio_file_path= file_path ,
                                        prompt=next_prompt)
    print("saving final transcripton")
    if format == tsFormats.JSON:
        return save_transcript_text_json(trx,f'{output_prefix}{file_path.stem}',dir=output_dir)


     
from utils import get_openai_client
from utils_transcribe import transcribe_audio_in_format
from utils_audio import chop_audio, convert_audio_to_ogg, open_audio_as_segment
from enums import RecordingFormats, RecordingTypes, tsFormats


   

class AudioFileMeta:
    def __init__(self, 
                 file_name:str,  #pk
                 input_file_format:RecordingFormats,
                 recording_type:RecordingTypes,
                 audio_length:float=None,
                 ) -> None:
        
        self.file_name = file_name
        self.input_file_format = input_file_format
        self.recording_type = recording_type
        self.audio_length = audio_length
        

class TranscriptMetadata:
    def __init__(self, 
                 audio_file_name:str,  #pk
                 transcript_format:tsFormats,
                 num_chunks:int=None,
                 org_name:str=None, 
                 audio_base_prompt:str=None,
                 speakers:dict=None
                 ) -> None:
        
        self.audio_file_name = audio_file_name
        self.transcript_format = transcript_format
        self.num_chunks = num_chunks
        self.org_name = org_name
        self.audio_base_prompt = audio_base_prompt
        self.speakers = speakers
        
class TranscriptChunk:
    def __init__(self,
                 id,
                 file_name,
                 text,
                 embedding=None) -> None:
        pass

raw_dir = DATA_DIR
ogg_dir = PROCESSED_DIR
audio_file = 'earning_call_morepen.mp3'
audio_type = RecordingTypes.CONCALL
audio_format = RecordingFormats.MP3

class AudioTranscript:
    def __init__(self,
                 text,
                 meta:dict) -> None:
        self.text = text 
        self.meta = meta 

# the following is one atomic chain 
def read_audio_file(file_name:str):
    ogg_file = convert_audio_to_ogg(file_name=file_name)
    if not ogg_file:
        raise Exception("Unable to convert audio to OGG")
   
    audio = open_audio_as_segment(ogg_file)
    total_duration_milliseconds = len(audio)
    total_duration_seconds = total_duration_milliseconds / 1000
    meta = AudioFileMeta(file_name=file_name,
                         input_file_format=RecordingFormats.MP3,
                         recording_type=RecordingTypes.CONCALL,
                         audio_length=total_duration_seconds)
    

    return meta, audio

def insert_audio_meta(meta:AudioFileMeta):
    pass

def transcribe_audio_in_chunks(audio_path:Path,
                                base_prompt:str,
                                output_dir=TS_DIR): # save text of each chunk (audio chunk)
    
    """ chop file and save chunks in chop dir. Finish transcription, concat transcripts and save in a AudioTranscript object to a json.
    ensure ogg file in full path is entered, base prompt to catch domain specific words.
        Transcribe each chunk sequentially reading from disk. 
        
    """
    meta = TranscriptMetadata(audio_file_name=audio_path.stem,
                              transcript_format=tsFormats.JSON)
    chunk_files = chop_audio(audio_path)
    meta.num_chunks = len(chunk_files)
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
            



## prepare a database to store the transcripts after processing chopped files 
## preferably faiss or mongo db ( embeddings will be stored there as well )

def insert_raw_transcript(chunk_meta):
    pass 


    
if __name__ == '__main__':
    f_chopped = 'earning_call_morepen_7.ogg'
    f_prmpt = 'earning_call_morepen_6.ogg'

    def test_transcribe_with_lag():
        file_path = Path(CHOP_DIR,f_chopped)
        file_path_p = Path(CHOP_DIR,f_prmpt)
        return transcribe_wth_lag_prompt(file_path=file_path,
                                         prompt_file=file_path_p,
                                         format=tsFormats.JSON)



    # print(test_transcribe_with_lag())
    
        