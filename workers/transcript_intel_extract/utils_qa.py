
from openai import OpenAI
import openai
import tiktoken

from handler_supabase import get_pdf_transcript_and_meta, insert_transcript_intel_entry
from config_qa import OPENAI_KEY

from pathlib import Path
import json
def insert_qa_section(file,results:list):
    qa_entry = { 'section_qa':results}
    return insert_transcript_intel_entry(file_name=file,
                                         qa_data=qa_entry)

def count_tokens(text, model="gpt-3.5-turbo"):
    encoding = tiktoken.encoding_for_model(model)
    tokens = encoding.encode(text)
    return len(tokens)


def get_openai_client():
    client = OpenAI(
        timeout=50.0,
        api_key=OPENAI_KEY)
    return client
    
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

def load_ts_section_management(file_name)->tuple:
    data = get_pdf_transcript_and_meta(file_name)
    key = data['addn_meta']['qa_start_key']
    d = data['extracted_transcript']
    keys = list(d.keys())
    print("key",key)
    split_index = keys.index(key)
    
    
    management_overview = {key: d[key] for key in keys[:split_index]}
    qa_section = {key: d[key] for key in keys[split_index+1:]}
    # x = qa_section.keys()
    # y = management_overview.keys()
    
    return management_overview

if __name__ =='__main__':
    # f = 'fy-2022_q3_earnings_call_transcript_pcbl_limited.pdf'
    f = 'fy25_q1_earnings_call_transcript_zomato_limited_zomato.pdf'

    def test_load_qa():
        return type(load_ts_sections(f))
    
    print(test_load_qa())