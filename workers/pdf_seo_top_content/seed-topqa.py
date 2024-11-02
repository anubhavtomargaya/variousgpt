from generate_content import service_extract_seo_top_questions
import pandas as pd
data = pd.read_csv('pdf-transcripts_rows.csv')
files = list(data['file_name'].dropna().to_list())
from db_supabase import get_distinct_transcript_files
skip = ['fy2025_q1_pvr_inox_limited_quarterly_earnings_call_transcript_pvrinox.pdf',
        'fy2024_q3_fortis_healthcare_limited_quarterly_earnings_call_transcript_fortis.pdf',
        'fy2024_q4_fortis_healthcare_limited_quarterly_earnings_call_transcript_fortis.pdf']

def main():
    files = get_distinct_transcript_files()
    for file in files:
        if file in skip:
            pass 
        else:

            try:

                print("running top qa for file:",file)
                r = service_extract_seo_top_questions(file_name=file)
                print(r)
            except Exception as e:
                print("Error in file ",file,e)
                pass 

    return True



if __name__=="__main__":
    # print(get_distinct_transcript_files())
    print(main())
    
