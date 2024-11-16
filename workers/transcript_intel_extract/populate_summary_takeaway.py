from gpt_app.common.supabase_handler import get_itdoc_mg_guidance
from handler_supabase import get_distinct_transcript_files
from summary_mg import  insert_management_intel
from utils_qa import load_ts_section_management
from generate_concall_summary_parent import generate_structured_summary
from generate_concall_summary_takeaway import generate_engaging_update


skip = [
    # 'fy-2024_q1_earnings_call_transcript_neuland_laboratories_524558.pdf.pdf',
    #  'fy-fy2024_q2_gravita_india_limited_quarterly_earnings_call_transcript_gravita.pdf',
    
]

def main():
    files = get_distinct_transcript_files()
    print("files len",len(files))
    for file in files:
        if file in skip:
            pass 
        else:

            try:

                key = 'struct_takeaway'
                print(f"running {key} for file:",file)
        
                m_summary = get_itdoc_mg_guidance(file, key='struct_summary')  
                s = generate_engaging_update(m_summary)
                if s:
                    print("inserting output",s)
                    r = insert_management_intel(file,key,s)
                    print("inserted")
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
    