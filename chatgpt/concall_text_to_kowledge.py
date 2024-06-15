from pathlib import Path
import json
from dirs import *
from utils_dir import _load_chunks_summary_doc, _save_embedded_doc, load_transcript_doc, save_summary_doc
from utils_process_text import split_document, count_words
from utils import get_openai_client
from utils_openai import get_embedding
from constants import DEFAULT_TEMPERATURE, DEFAULT_TOP_P
from dirs import PROCESSED_DIR,TS_DIR
from transcribe import transcribe_audio_in_chunks

ogg_file= 'earning_call_morepen.ogg'

def get_base_prompt(morepen=True):
    if morepen:
        return "Embarking on a transformative journey over four decades, Morepen has consistently strived to embody an \
            organization marked by discernible, impactful differences. Every action we undertake is imbued with a profound \
                commitment to enrich the lives we touch. Nestled amidst the serene surroundings of Baddi, our cutting-edge manufacturing facility \
                boasts a scientifically integrated complex housing 10 plants, each tailored to produce specific product lines."
    else:
        return ""
    
def create_transcript_from_processed_audio(ogg_file, source_dir=PROCESSED_DIR):
    processed_audio_path = Path(source_dir,ogg_file)

    output_file = transcribe_audio_in_chunks(base_prompt=get_base_prompt(),
                                             audio_path=processed_audio_path,
                                             output_dir=TS_DIR)
    print("successfully transcribed and saved to",TS_DIR)
    print(output_file)

## saved as raw text -> after this point ether give to gpt4o for diarization in chunks 
# or give to user for annotating.

## prcess-text.ipnyb

## summarise-big-text-into-mini-corpus

def identify_section_and_summarize(client, chunk, model="gpt-3.5-turbo")->str:

    response = client.chat.completions.create(
                                                model=model,
                                                messages=[{
                                                            "role": "system", "content": "You are a helpful assistant to summarise an EARNINGS CONFERENCE CALL. The transcript of the call will be provided in chunks. Identify sections out of the Sections : [INTRO, MANAGEMENT NOTE, ANALYST QA, CONCLUSION]. Assign a tag to each section only out of these. Also summarise the chunk. Return the data in form of JSON `{section : '', summary: '' }`.  I repeat -- FOLLOW THE FORMAT OF JSON AND CHOOSE SECTION FROM PROVIDED SECTIONS ONLY. KEEP THE SUMMARY DETAILED AND AROUNDO 300 words.",
                                                        },
                                                        {"role": "user", "content": f"Identify the section and summarize the following text:\n\n{chunk}\n\n"
                                                        }],
                                                temperature=DEFAULT_TEMPERATURE,
                                                max_tokens=300,
                                                top_p=DEFAULT_TOP_P
                                            )
  
    response_content = response.choices[0].message.content
    return response_content

def process_document_chunks(chunks)->dict:
    client = get_openai_client()
    doc_meta = { }
    print("running gpt on the chunks, num chunks :", len(chunks))
    for i in range(len(chunks)):
        print("processing: ",i,'...') 
        current_chunk = chunks[i]
        res = identify_section_and_summarize(client=client, chunk=current_chunk) ## return a json but in string -> make the above func better by 21
        try:
            doc_t = res.removeprefix('```json') # try catch
            ddict =json.loads( doc_t.removesuffix('```'))
        except Exception as e:
            print(e)
            print(":::",res) 
            ddict = {'section':None, 'summary':None}

        chunk_summary_meta =  {'chunk_text':current_chunk ,
                            'section':ddict['section'],
                            'summary':ddict['summary']
                          }
        doc_meta[i]=chunk_summary_meta
    return doc_meta

    
def create_embeddings_from_chunk_doc(client, 
                                     filename,
                                     text_column='chunk_text'):
    doc = _load_chunks_summary_doc(filename)
    embedded_doc = doc
    for k,v in doc.items():
        print("embedding k",k)
        embedded_doc[k]['embedding'] = get_embedding(client,
                                                     embedded_doc[k][text_column]) 
        
    return _save_embedded_doc(embedded_doc,filename)

## save the embedded doc
# save_summary(doc,f'embedded_{file_name}')

if __name__ =='__main__':
    filename = 'conc_earning_call_morepen.json'
    def test_load_ts():
        tx = load_transcript_doc(filename)
  
        return count_words(tx)


    def test_summarise_doc_chunks():
        doc = load_transcript_doc(filename=filename)
        chunks = split_document(doc,chunk_size=3500,overlap=100)
        print("num chunks", len(chunks))
        doc_sum_ = process_document_chunks(chunks)
        return save_summary_doc(doc_sum_,filename=filename)

    def test_embed_chunk_summary_doc():
        client = get_openai_client()
        return create_embeddings_from_chunk_doc(client,filename=filename)
    

    # print(test_load_ts())
    # print(test_summarise_doc_chunks())
    print(test_embed_chunk_summary_doc())



