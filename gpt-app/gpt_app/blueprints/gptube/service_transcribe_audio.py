
from pathlib import Path

from  gpt_app.common.utils_audio import convert_audio_to_ogg,chop_audio
from  gpt_app.common.utils_openai import get_openai_client
from  gpt_app.common.utils_dir import check_ts_dir, save_transcript_text_json
from  gpt_app.common.dirs import DATA_DIR,  PROCESSED_DIR, YOUTUBE_DIR,TS_DIR,CHOP_DIR
from  gpt_app.common.models import  AudioTranscript, TranscriptMetadata
from  gpt_app.common.enums import  tsFormats
from gpt_app.blueprints.gptube.gpt_service import transcribe_audio_in_format


def transcribe_audio_in_chunks(audio_path:Path,
                                base_prompt:str,
                                source_dir = YOUTUBE_DIR,
                                output_dir=TS_DIR): # save text of each chunk (audio chunk)
    
    """ chop file and save chunks in chop dir. Finish transcription, concat transcripts and save in a AudioTranscript object to a json.
    ensure ogg file in full path is entered, base prompt to catch domain specific words.
        Transcribe each chunk sequentially reading from disk. 
        
    """
    meta = TranscriptMetadata(audio_file_name=audio_path.stem,
                              transcript_format=tsFormats.JSON)
    fmt = audio_path.name.split('.')[-1]
    chunk_files = chop_audio(audio_path,source_dir=source_dir,format=fmt)
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
    else:
         raise Exception("Error while saving text as json")


        
def create_text_from_audio(file_name:Path,
                            base_prompt='',
                            youtube=False
                                  ):
    source_dir = YOUTUBE_DIR if youtube else DATA_DIR
    if check_ts_dir(file_name):
        print(check_ts_dir(file_name))
        return file_name
    else:
        # ogg_file = convert_audio_to_ogg(file_name=file_name,data_dir=source_dir)
        # if ogg_file:
            # print(ogg_file)

            return transcribe_audio_in_chunks(audio_path=Path(source_dir,file_name   ), 
                                        base_prompt=base_prompt) 
    

    
if __name__ == '__main__':

    def test_service_create_text_from_audio():
        # file = "Neuland_Laboratories_Ltd_Q4_FY2023-24_Earnings_Conference_Call.mp4"
        # base_prmpt_neu = "Conference Call Insights Unlock the Future of Market Intelligence with AlphaStreet! Our revolutionary global ecosystem connects public companies, investors, analysts, and experts. At AlphaStreet, our mission is to empower our constituents to build robust connections and harness cutting-edge technology for insightful, data-driven decision making.\n\n\nDiscover the power of AI-driven AlphaStreet Intelligence, your gateway to services, research, and insights. Get real-time access to earnings and conference calls, interact with experts, engage with management/analysts/investor, all within one platform. Embrace innovation with our latest AI technology that allows for precision research from live and historical information and data. Zero in on insights from automatic topic categorization and on-demand summaries from a wealth of financial content. Additionally, experience generative AI for conversational interaction.\n\nAlphaStreet levels the playing field, giving you a strategic advantage in market intelligence. Join AlphaStreet, where we are uniting companies, analysts, investors, and experts to foster valuable interactions and shared insights."
        # file = "Juan_Camilo_Avendano_and_Ankit_Gupta.mp3"
        file = 'Avanti_Feeds_Ltd_Q4_FY2023-24_Earnings_Conference_Call.mp4'
        base_prmpt = "INTERVIEW CALL BETWEEN TWO PEOPLE:" + file 
        return create_text_from_audio(file_name=file,base_prompt=base_prmpt,youtube=False)
    
    print(test_service_create_text_from_audio())