
from datetime import datetime
from pathlib import Path
import tempfile
import google
from  gpt_app.common.utils_audio import convert_audio_to_ogg,open_audio_as_segment,chop_audio
from  gpt_app.common.utils_openai import get_openai_client
from  gpt_app.common.utils_dir import _make_file_path, check_blob, check_ts_dir, save_transcript_text_json, upload_blob_to_gcs_bucket_by_filename
from  gpt_app.common.dirs import BUCKET_NAME, DATA_DIR,  PROCESSED_DIR, YOUTUBE_DIR,TS_DIR,CHOP_DIR
from  gpt_app.common.models import  AudioTranscript, TranscriptMetadata
from  gpt_app.common.enums import  tsFormats
from gpt_app.blueprints.gptube.gpt_service import transcribe_audio_in_format
from gpt_app.blueprints.gptube.service_process_to_ogg import convert_local_path_to_ogg_with_ffmpeg
from gpt_app.common.supabase_handler import check_ts_exist, insert_ts_entry
from gpt_app.common.session_manager import get_user_email

def transcribe_gcs_audio(gcs_client,
                         audio_file,
                         dir=PROCESSED_DIR,
                         format=None,
                         prompt="",
                         db=False):
    try:
        
        bucket = gcs_client.bucket(BUCKET_NAME)
        
      
        audio_file_gcs = _make_file_path(dir,
                                        audio_file,
                                        format=format,
                                        local=False)
        openai_client = get_openai_client()
        openai_client.timeout = 100000
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            blob = bucket.blob(audio_file_gcs)
            exists = blob.exists()
            print(f"Exists: {exists}")
            afile = Path(PROCESSED_DIR,audio_file).as_posix()
            blob.download_to_filename(afile)
            file_path = temp_file.name
        st = datetime.utcnow()
        transcript_final = AudioTranscript(text='',meta={'total_chunks':1,
                                                    'count':0 
                                                    }
                                        )
       
        with open(afile, 'rb') as af:

            print("calling open api start.")
            transcription = openai_client.audio.transcriptions.create( model= "whisper-1", file=af,
                                                        response_format=tsFormats.JSON.value,
                                                        prompt=prompt
                                                            )
        # if db:
            # ttl = Path(audio_file).as_posix().split('.')[0]
            # e_ = insert_ts_entry(title=ttl,
            #                      text=transcription.text,
            #                      added_by=get_user_email())
            # print("E_",e_)
            # return ttl if e_ else False
        # else:
        transcript_final.text=transcription
        print("calling open api end.")
        et = datetime.utcnow()
        total_time = et - st
        print("total processing time ", total_time.seconds, 'seconds')
        print("total cost $", round(0.006*total_time.seconds),2)

        fpath = save_transcript_text_json(transcription,
                                        audio_file,
                                        dir=TS_DIR,
                                        added_by=get_user_email())
        if fpath:
            print(id, "file processsed as ts: ", fpath.stem)
            return upload_blob_to_gcs_bucket_by_filename(gcs_client,fpath,TS_DIR,format='json')
            return f'{out_file_name}.json'
        else:
            raise Exception("Error! not fpath")



    except google.api_core.exceptions.NotFound as e:
        print(f"Error: Audio file '{audio_file}' not found.")
        raise Exception("GCS FILE NOT FOUND: %s",e.__str__())
    
    except Exception as e:

        raise Exception("Error while saving text as json")


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
    meta = TranscriptMetadata(audio_file_name=audio_path.stem,
                              transcript_format=tsFormats.JSON)
    fmt = audio_path.name.split('.')[-1]
    # chunk_files =  [ open_audio_as_segment(audio_path,)]
    chunk_files = chop_audio(audio_path,source_dir=source_dir,format=fmt,n_minutes=n_mins)
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


from gpt_app.common.utils_dir import client as gcs_client,_make_file_path
def create_text_from_audio(file_name:Path,
                            base_prompt='',
                            source_dir= YOUTUBE_DIR 
                        ):
    #TODO 


    file_name = Path(file_name)
    destination_blob_path  = _make_file_path(TS_DIR,
                                file_name,
                                local=False)
    print('dest path:')
    print(destination_blob_path) 
    # check if the transcript exists in TS DIR , return the path if it does
    if check_blob(gcs_client=gcs_client,
                  destination_blob_name=destination_blob_path):
        return destination_blob_path
    
    ogg_dir = PROCESSED_DIR
    fname = convert_local_path_to_ogg_with_ffmpeg(file_path=Path(source_dir,file_name),output_dir=ogg_dir)
    print("ogg converted!")
    trx = transcribe_gcs_audio(gcs_client=gcs_client,
                               audio_file=Path(fname),
                               dir=ogg_dir,
                               format='ogg',
                               prompt=f"{base_prompt} : {Path(file_name).name} ")
    print("dest:",trx)

    return trx

    
        # #all local 
        # # if check_ts_dir(file_name):
        #     # print(check_ts_dir(file_name))
        #     # return file_name.as_posix().split('.')[0]
        # # else:
        # if ogg:
            
        #     fname = convert_audio_to_ogg(file_name=file_name,
        #                                 source_dir=source_dir,
        #                                 local=True)
        #     source_dir = PROCESSED_DIR
        # else:
        #     fname = file_name
        # print("FILEN ",fname)
        # print(source_dir,fname)
        # return transcribe_audio_in_chunks(audio_path=Path(source_dir,fname), 
        #                                     base_prompt=base_prompt,n_mins=15) 
        

    
if __name__ == '__main__':

    from gpt_app.common.utils_dir import client as gcs_client
    def test_service_create_text_from_audio():
        # file = "Neuland_Laboratories_Ltd_Q4_FY2023-24_Earnings_Conference_Call.mp4"
        # base_prmpt_neu = "Conference Call Insights Unlock the Future of Market Intelligence with AlphaStreet! Our revolutionary global ecosystem connects public companies, investors, analysts, and experts. At AlphaStreet, our mission is to empower our constituents to build robust connections and harness cutting-edge technology for insightful, data-driven decision making.\n\n\nDiscover the power of AI-driven AlphaStreet Intelligence, your gateway to services, research, and insights. Get real-time access to earnings and conference calls, interact with experts, engage with management/analysts/investor, all within one platform. Embrace innovation with our latest AI technology that allows for precision research from live and historical information and data. Zero in on insights from automatic topic categorization and on-demand summaries from a wealth of financial content. Additionally, experience generative AI for conversational interaction.\n\nAlphaStreet levels the playing field, giving you a strategic advantage in market intelligence. Join AlphaStreet, where we are uniting companies, analysts, investors, and experts to foster valuable interactions and shared insights."
        # file = "Juan_Camilo_Avendano_and_Ankit_Gupta.mp3"
        f= 'Avanti_Feeds_Ltd_Q4_FY2023-24_Earnings_Conference_Call.mp4'
        # f = 'Budget_पर_Kharge_ने_Rajya_Sabha_में__सुनाया_गुस्से_में_Nirmala_Sitharaman_ने_क्या_गिना_दिया.webm'
        # base_prmpt = "INTERVIEW CALL BETWEEN TWO PEOPLE:" + file 
        return create_text_from_audio(file_name=f)
    
    # fk ='Raymond Ltd Q4 FY2023-24 Earnings Conference Call.ogg'
    def test_gcs_transcribe():
        return transcribe_gcs_audio(gcs_client=gcs_client,
                             audio_file=Path(f),format='ogg',prompt=' '.join(fk.split('_')[0:-1]))
    
    print(test_service_create_text_from_audio())
    # print(test_gcs_transcribe())