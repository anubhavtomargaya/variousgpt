from handler_supabase import get_distinct_transcript_files
from summary_mg import extract_management_insights, insert_summary_management
from utils_qa import load_ts_section_management


skip = ['fy2025_q1_pondy_oxides_and_chemicals_limited_quarterly_earnings_call_transcript_pocl.pdf',
     'fy-2025_q1_earnings_call_transcript_asian_paints_500820.pdf',
     'Q4_FY23_Earnings_Conference_Raymond_Limited.pdf'
]

def main():
    files = get_distinct_transcript_files()
    print("files len",len(files))
    for file in files:
        if file in skip:
            pass 
        else:

            try:

                key = 'structured_guidance'
                print(f"running {key} for file:",file)
        # key = 'structured_summary'
                section = load_ts_section_management(file)
                s = extract_management_insights(section)
                if s:
                    print("inserting")
                    r = insert_summary_management(file,s,key=key)
                    print(r)
                else:
                    print("not found")
                    
                    return None
            except Exception as e:
                print("Error in file ",file,e)
                pass 

    return True



if __name__=="__main__":
    # print(get_distinct_transcript_files())
    print(main())
    