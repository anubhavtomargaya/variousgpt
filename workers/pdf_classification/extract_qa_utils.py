
from extract_qa_supabase import get_pdf_transcript_and_meta
def load_ts_sections(file_name)->tuple:
    data = get_pdf_transcript_and_meta(file_name)
    key = data['addn_meta']['qa_start_key']
    d = data['extracted_transcript']
    keys = list(d.keys())
    split_index = keys.index(key)
    
    
    management_overview = {key: d[key] for key in keys[:split_index]}
    qa_section = {key: d[key] for key in keys[split_index+1:]}
    x = qa_section.keys()
    y = management_overview.keys()
    
    return x,y

if __name__ =='__main__':
    # f = 'fy-2022_q3_earnings_call_transcript_pcbl_limited.pdf'
    f = 'fy25_q1_earnings_call_transcript_zomato_limited_zomato.pdf'

    def test_load_qa():
        return type(load_ts_sections(f))
    
    print(test_load_qa())