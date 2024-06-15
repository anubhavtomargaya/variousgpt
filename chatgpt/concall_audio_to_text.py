
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
        # file = "Neuland_Laboratories_Ltd_Q4_FY2023-24_Earnings_Conference_Call.mp4"
        # base_prmpt_neu = "Conference Call Insights Unlock the Future of Market Intelligence with AlphaStreet! Our revolutionary global ecosystem connects public companies, investors, analysts, and experts. At AlphaStreet, our mission is to empower our constituents to build robust connections and harness cutting-edge technology for insightful, data-driven decision making.\n\n\nDiscover the power of AI-driven AlphaStreet Intelligence, your gateway to services, research, and insights. Get real-time access to earnings and conference calls, interact with experts, engage with management/analysts/investor, all within one platform. Embrace innovation with our latest AI technology that allows for precision research from live and historical information and data. Zero in on insights from automatic topic categorization and on-demand summaries from a wealth of financial content. Additionally, experience generative AI for conversational interaction.\n\nAlphaStreet levels the playing field, giving you a strategic advantage in market intelligence. Join AlphaStreet, where we are uniting companies, analysts, investors, and experts to foster valuable interactions and shared insights."
        file = "Juan_Camilo_Avendano_and_Ankit_Gupta.mp3"
        base_prmpt = "INTERVIEW CALL BETWEEN TWO PEOPLE:" + file 
        return create_text_from_audio(file_name=file,base_prompt=base_prmpt,youtube=False)
    
    print(test_service_create_text_from_audio())