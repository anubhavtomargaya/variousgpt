from pathlib import Path
from models import AudioFileMeta, AudioTranscript, TranscriptMetadata
from utils_dir import save_transcript_text_json
from dirs import *
from utils import get_openai_client
from utils_transcribe import transcribe_audio_in_format
from utils_audio import chop_audio, convert_audio_to_ogg, open_audio_as_segment
from enums import RecordingFormats, RecordingTypes, tsFormats


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


     

        
raw_dir = DATA_DIR
ogg_dir = PROCESSED_DIR
audio_file = 'earning_call_morepen.mp3'
audio_type = RecordingTypes.CONCALL
audio_format = RecordingFormats.MP3


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
    file = "Neuland_Laboratories_Ltd_Q4_FY2023-24_Earnings_Conference_Call.mp4"
    
    base_prmpt_neu = "Conference Call Insights Unlock the Future of Market Intelligence with AlphaStreet! Our revolutionary global ecosystem connects public companies, investors, analysts, and experts. At AlphaStreet, our mission is to empower our constituents to build robust connections and harness cutting-edge technology for insightful, data-driven decision making.\n\n\nDiscover the power of AI-driven AlphaStreet Intelligence, your gateway to services, research, and insights. Get real-time access to earnings and conference calls, interact with experts, engage with management/analysts/investor, all within one platform. Embrace innovation with our latest AI technology that allows for precision research from live and historical information and data. Zero in on insights from automatic topic categorization and on-demand summaries from a wealth of financial content. Additionally, experience generative AI for conversational interaction.\n\nAlphaStreet levels the playing field, giving you a strategic advantage in market intelligence. Join AlphaStreet, where we are uniting companies, analysts, investors, and experts to foster valuable interactions and shared insights."
    def test_transcribe_with_lag():
        file_path = Path(CHOP_DIR,f_chopped)
        file_path_p = Path(CHOP_DIR,f_prmpt)
        return transcribe_wth_lag_prompt(file_path=file_path,
                                         prompt_file=file_path_p,
                                         format=tsFormats.JSON)


    def test_transcribe_ini_chunks():
        return transcribe_audio_in_chunks(audio_path=Path(YOUTUBE_DIR,file), 
                                          base_prompt=base_prmpt_neu) 
    # print(test_transcribe_with_lag())
    print(test_transcribe_ini_chunks())
    
        