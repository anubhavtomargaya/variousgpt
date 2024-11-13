from handler_supabase import get_distinct_transcript_files
from summary_mg import  insert_management_intel
from utils_qa import load_ts_section_management
from generate_concall_summary_parent import generate_structured_summary


skip = ['fy-2024_q1_earnings_call_transcript_neuland_laboratories_524558.pdf.pdf',
     'fy-fy2024_q2_gravita_india_limited_quarterly_earnings_call_transcript_gravita.pdf',
    
]

def main():
    files = get_distinct_transcript_files()
    print("files len",len(files))
    for file in files:
        if file in skip:
            pass 
        else:

            try:

                key = 'struct_summary'
                print(f"running {key} for file:",file)
        # key = 'structured_summary'
                section = load_ts_section_management(file)
                s = generate_structured_summary(section)
                if s:
                    print("inserting")
                    r = insert_management_intel(file,key,s)
                    print("inserted",len(r))
                    # print(r)
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
    