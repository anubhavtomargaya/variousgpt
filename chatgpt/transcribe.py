from pathlib import Path
from dirs import *
from utils import get_openai_client
from utils_transcribe import transcribe_audio_in_format, write_trx_as_json, write_trx_as_subtitles
from enums import tsFormats

def transcribe_and_save(file_path:Path, 
                        output_dir=TS_DIR,
                        format:tsFormats=tsFormats.JSON,
                        prompt:str="",
                        output_prefix=None,):
    # client = get_openai_client()
    print("starting transcription:..")
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
    f_chopped = 'earning_call_morepen_8.ogg'

    def test_transcribe_and_save_chopped_file():
        file_path = Path(CHOP_DIR,f_chopped)
        return transcribe_and_save(file_path=file_path,format=tsFormats.JSON)
    
    print(test_transcribe_and_save_chopped_file())
    
        