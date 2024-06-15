
from pathlib import Path
from transcribe import transcribe_audio_in_chunks
from utils_audio import convert_audio_to_ogg
from dirs import DATA_DIR,  PROCESSED_DIR, YOUTUBE_DIR

def create_text_from_audio(file_name,
                            base_prompt='',
                            youtube=False
                                  ):
    source_dir = YOUTUBE_DIR if youtube else DATA_DIR
    ogg_file = convert_audio_to_ogg(file_name=file_name,data_dir=source_dir)
    if ogg_file:
        print(ogg_file)

        return transcribe_audio_in_chunks(audio_path=Path(PROCESSED_DIR,ogg_file   ), 
                                        base_prompt=base_prompt) 
    

if __name__ == '__main__':

    def test_service_create_text_from_audio():
        file = "Neuland_Laboratories_Ltd_Q4_FY2023-24_Earnings_Conference_Call.mp4"
        base_prmpt_neu = "Neuland_Laboratories_Ltd_Q4_FY2023-24_Earnings_Conference_Call"

        return create_text_from_audio(file_name=file,base_prompt=base_prmpt_neu,youtube=True)
    
    print(test_service_create_text_from_audio())