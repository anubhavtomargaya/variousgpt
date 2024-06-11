from pathlib import Path
from dirs import *
from utils import get_openai_client
from utils_transcribe import transcribe_audio_in_format, write_trx_as_json, write_trx_as_subtitles
from enums import tsFormats

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
        return write_trx_as_json(trx,f'{output_prefix}{file_path.stem}',dir=output_dir)

def transcribe_and_save(file_path:Path, 
                        prompt:str="",
                        format:tsFormats=tsFormats.JSON,
                        output_dir=TS_DIR,
                        output_prefix=None,):
    # client = get_openai_client()
    print("starting transcription :..")
    trx = transcribe_audio_in_format(client=get_openai_client(),
                                        audio_file_path= file_path ,
                                        prompt=prompt)
    print("type")
    print(type(trx))
    print(trx)
    if format == tsFormats.JSON:

        return write_trx_as_json(trx,f'{output_prefix}{file_path.stem}',dir=output_dir)
    
    if format == tsFormats.SRT:
        return write_trx_as_subtitles(trx,file_path.stem)
     
if __name__ == '__main__':
    f_chopped = 'earning_call_morepen_7.ogg'
    f_prmpt = 'earning_call_morepen_6.ogg'

    def test_transcribe_and_save_chopped_file():
        file_path = Path(CHOP_DIR,f_chopped)
        return transcribe_and_save(file_path=file_path,format=tsFormats.JSON,output_prefix="cwp")
    
    def test_transcribe_with_lag():
        file_path = Path(CHOP_DIR,f_chopped)
        file_path_p = Path(CHOP_DIR,f_prmpt)
        return transcribe_wth_lag_prompt(file_path=file_path,
                                         prompt_file=file_path_p,
                                         format=tsFormats.JSON)


    print(test_transcribe_and_save_chopped_file())
    # print(test_transcribe_with_lag())
    
        