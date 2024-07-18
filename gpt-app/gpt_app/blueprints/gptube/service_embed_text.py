from pathlib import Path
import json
import tiktoken
from openai import OpenAIError

from gpt_app.common.dirs import *
from gpt_app.common.utils_dir  import _load_chunks_segment_doc, _load_chunks_summary_doc, _save_embedded_doc, load_transcript_doc, save_diarize_doc, save_questions_doc, save_segment_doc, save_summary_doc, upload_blob_to_gcs_bucket_by_filename
from gpt_app.common.utils_text import split_document, count_words
from gpt_app.common.utils_openai import get_openai_client, get_embedding

from gpt_app.common.constants import DEFAULT_TEMPERATURE, DEFAULT_TOP_P

# ogg_file= 'earning_call_morepen.ogg'
# utils 
def get_base_prompt(morepen=True):
    if morepen:
        return "Embarking on a transformative journey over four decades, Morepen has consistently strived to embody an \
            organization marked by discernible, impactful differences. Every action we undertake is imbued with a profound \
                commitment to enrich the lives we touch. Nestled amidst the serene surroundings of Baddi, our cutting-edge manufacturing facility \
                boasts a scientifically integrated complex housing 10 plants, each tailored to produce specific product lines."
    else:
        return ""
    
# def create_transcript_from_processed_audio(ogg_file, source_dir=PROCESSED_DIR):
#     processed_audio_path = Path(source_dir,ogg_file)

#     output_file = transcribe_audio_in_chunks(base_prompt=get_base_prompt(),
#                                              audio_path=processed_audio_path,
#                                              output_dir=TS_DIR)
#     print("successfully transcribed and saved to",TS_DIR)
#     print(output_file)

## saved as raw text -> after this point ether give to gpt4o for diarization in chunks 
# or give to user for annotating.

## prcess-text.ipnyb

## summarise-big-text-into-mini-corpus
summary_prmpt = "You are a helpful assistant to summarise a quarterly EARNINGS CONFERENCE CALL. The transcript of the call will be provided in chunks as context and you have to extract information carefully and concisely in summaries.  "
sections_interview =  ['INTRO', 'MANAGEMENT NOTE', 'ANALYST QA', 'CONCLUSION']


summary_prmpt_interview = "You are a helpful assistant to aid a USER INTERVIEW CALL. The transcript of the call will be provided in chunks \
                         Provide the summary highlihgting the sentiments and possible pain points of the user.  \
                            Remember that the Interviewr is A PRODUCT MANAGER and the other person is a CHURNED OUT USER OF THE APP SCISPACE"
sections_interview = ['INTRO','QA','DISCUSSION','TAKEAWAYS']


def identify_section_and_summarize(client,
                                    chunk,
                                    summariser_prompt="you are a helpful assistant to summarise the provided text.",
                                    sections=sections_interview,
                                    model="gpt-3.5-turbo")->str:

    response = client.chat.completions.create(
                                                model=model,
                                                messages=[{
                                                            "role": "system", "content": f"{summariser_prompt} Identify sections out of the Sections :{sections}. Assign a tag to each section only out of these.  Return the data in form of JSON -- section : '', summary: '' ` --   I repeat -- FOLLOW THE FORMAT OF JSON AND CHOOSE SECTION FROM PROVIDED SECTIONS ONLY. .",
                                                        },
                                                        {"role": "user", "content": f"Identify the section and summarize the following text:\n\n{chunk}\n\n"
                                                        }],
                                                temperature=1.2,
                                                max_tokens=300,
                                                top_p=DEFAULT_TOP_P,
                                                response_format={'type': 'json_object'}
                                            )
  
    response_content = response.choices[0].message.content
    
    return response_content

def gpt_diarize_chunks(client,
                        chunk,
                        prev_diz=None,
                        dizer_prompt="you are a helpful assistant to diarize the provided transcript text.",
                        model="gpt-3.5-turbo")->str:
    my_messages = [
                    {   "role": "system", "content": f"{dizer_prompt}",  },
                    {   "role": "system", "content": f"The diarization of previous chunk: {prev_diz}. ",},
                    {   "role": "user", "content": f"Return the diarized text.  Diarize and extract speaker by turn in the following text:\n\n{chunk}\n\n "}
                ]
    all_content = " ".join([msg["content"] for msg in my_messages])

    # Tokenize the concatenated content
    encoding = tiktoken.get_encoding("cl100k_base")
    tokens = encoding.encode(all_content)

    # Print the tokens
    print(f"Number of tokens: {len(tokens)}")
    # print(f"Tokens: {tokens}")

    try:
        response = client.chat.completions.create(
            model=model,
            messages=my_messages,
            temperature=1.2,
            max_tokens=1000,
            top_p=DEFAULT_TOP_P
        )

        response_content = response.choices[0].message.content

        return response_content
    except OpenAIError as e:
        print(f"An error occurred: {e}")
        return None

def gpt_segment_chunks(client,
                        chunk,
                        prev_seg=None,
                        prev_chunk=None,
                        dizer_prompt="you are a helpful assistant to diarize the provided transcript text.",
                        model="gpt-3.5-turbo")->str:
    my_messages = [
                    {   "role": "system", "content": f"{dizer_prompt}",  },
                    {   "role": "system", "content": f"previous chunk: {prev_chunk} \
                                                    identified segment of previous chunk {prev_seg}. ",},

                    {   "role": "user", "content": f"Return the response text IN ABOVE JSON FORMAT ONLY .\
                                                    Extract the described segments in format for the following trascript  chunk:\n\n{chunk}\n\n "}
                ]
    all_content = " ".join([msg["content"] for msg in my_messages])

    # Tokenize the concatenated content
    encoding = tiktoken.get_encoding("cl100k_base")
    tokens = encoding.encode(all_content)

    # Print the tokens
    print(f"Number of tokens: {len(tokens)}")
    # print(f"Tokens: {tokens}")

    try:
        response = client.chat.completions.create(
            model=model,
            messages=my_messages,
            temperature=1.2,
            max_tokens=1000,
            top_p=DEFAULT_TOP_P,
            response_format={'type': 'json_object'}
        )

        response_content = response.choices[0].message.content

        return response_content
    except OpenAIError as e:
        print(f"An error occurred: {e}")
        return None

def gpt_qa_digest_chunks(client,
                        chunk,
                        prev_chunk=None,
                        dizer_prompt="you are a helpful assistant to diarize the provided transcript text.",
                        model="gpt-3.5-turbo")->str:
    my_messages = [
                    {   "role": "system", "content": f"{dizer_prompt}",  },
                    {   "role": "system", "content": f"previous: {prev_chunk} \
                                                    ",},

                    {   "role": "user", "content": f"chunk:\n\n{chunk}\n\n "}
                ]
    all_content = " ".join([msg["content"] for msg in my_messages])

    # Tokenize the concatenated content
    encoding = tiktoken.get_encoding("cl100k_base")
    tokens = encoding.encode(all_content)

    # Print the tokens
    print(f"Number of tokens: {len(tokens)}")
    # print(f"Tokens: {tokens}")

    try:
        response = client.chat.completions.create(
            model=model,
            messages=my_messages,
            temperature=1.2,
            max_tokens=2000,
            top_p=DEFAULT_TOP_P,
           
        )

        response_content = response.choices[0].message.content

        return response_content
    except OpenAIError as e:
        print(f"An error occurred: {e}")
        return None

def gpt_filter_analyst_questions(client,
                       text,

                        system_prompt="you are a helpful assistant to diarize the provided transcript text.",
                        model="gpt-3.5-turbo")->str:
    my_messages = [
                    {   "role": "system", "content": f"{system_prompt}",  },

                    {   "role": "user", "content": f":\n\n{text}\n\n "}
                ]
    all_content = " ".join([msg["content"] for msg in my_messages])

    # Tokenize the concatenated content
    encoding = tiktoken.get_encoding("cl100k_base")
    tokens = encoding.encode(all_content)

    # Print the tokens
    print(f"Number of tokens: {len(tokens)}")
    # print(f"Tokens: {tokens}")

    try:
        response = client.chat.completions.create(
            model=model,
            messages=my_messages,
            temperature=1.2,
            max_tokens=2000,
            top_p=DEFAULT_TOP_P,
            response_format={'type': 'json_object'}
           
        )

        response_content = response.choices[0].message.content

        return response_content
    except OpenAIError as e:
        print(f"An error occurred: {e}")
        return None

def gpt_summarise_qa_digest_doc(client,
                        chunk,

                        dizer_prompt="you are a helpful assistant to diarize the provided transcript text.",
                        model="gpt-3.5-turbo")->str:
    my_messages = [
                    {   "role": "system", "content": f"{dizer_prompt}",  },

                    {   "role": "user", "content": f"chunk :\n\n{chunk}\n\n "}
                ]
    all_content = " ".join([msg["content"] for msg in my_messages])

    # Tokenize the concatenated content
    encoding = tiktoken.get_encoding("cl100k_base")
    tokens = encoding.encode(all_content)

    # Print the tokens
    print(f"Number of tokens: {len(tokens)}")
    # print(f"Tokens: {tokens}")

    try:
        response = client.chat.completions.create(
            model=model,
            messages=my_messages,
            temperature=1.2,
            max_tokens=2000,
            top_p=DEFAULT_TOP_P,
           
        )

        response_content = response.choices[0].message.content

        return response_content
    except OpenAIError as e:
        print(f"An error occurred: {e}")
        return None
    
def gpt_summarise_document_chunks(chunks,
                                  summariser_prompt,
                                  sections)->dict:
    client = get_openai_client()
    doc_meta = { }
    print("running gpt on the chunks, num chunks :", len(chunks))
    for i in range(len(chunks)):
        print("processing: ",i,'...') 
        current_chunk = chunks[i]
        res = identify_section_and_summarize(client=client,
                                             chunk=current_chunk,
                                             summariser_prompt=summariser_prompt,
                                             sections=sections) ## return a json but in string -> make the above func better by 21
        try:
            print("res:",res)
            print("type",type(res))
            if res.startswith("```json") and res.endswith("`"):
  # Remove starting and ending markers (without using removeprefix/removesuffix)
                start = len("```json")
                end = res.rfind("```")
                doc_t = res[start:end]  # Extract text between markers

                # Load JSON data
                try:
                    ddict = json.loads(doc_t)
                    # Process the loaded dictionary (ddict)
                    print("Dictionary:", ddict)
                except json.JSONDecodeError:
                    print("Invalid JSON format")
            else:
                ddict = json.loads(res)
                print("String does not start or end with markers")
        except Exception as e:
            print(e)
            print(":::",res) 
            res = json.loads(res)
            ddict = {'section':None, 'summary':None}

        chunk_summary_meta =  {'chunk_text':current_chunk ,
                                'section':ddict['section'],
                                'summary':ddict['summary']
                          }
        doc_meta[i]=chunk_summary_meta
    return doc_meta

def gpt_diarize_document_chunks(chunks,
                                  dizer_prompt,
                                  )->dict:
    client = get_openai_client()
    doc_meta = { }
    print("running gpt on the chunks, num chunks :", len(chunks))
    prev_diazrize = None
    for i in range(len(chunks)):
        print("processing: ",i,'...') 
        current_chunk = chunks[i]
        res = gpt_diarize_chunks(client=client,
                                 prev_diz=prev_diazrize,
                                chunk=current_chunk,
                                dizer_prompt=dizer_prompt,
                                            )
        try:
            print("res:",res)
            print("type",type(res))
           
            dtext = str(res)

        except Exception as e:
            print(e)
    
            dtext = str('')

        chunk_diarized =  {'chunk_text':current_chunk ,
                                'diarize':dtext
                          }
        prev_diazrize = chunk_diarized
        doc_meta[i]=chunk_diarized
    return doc_meta

def gpt_segment_document_chunks(chunks,
                                segger_prompt,
                                  )->dict:
    client = get_openai_client()
    doc_meta = { }
    print("running gpt on the chunks, num chunks :", len(chunks))
    prev_segment = None
    prev_chunk = None
    for i in range(len(chunks)):
        print("processing: ",i,'...') 
        current_chunk = chunks[i]
        res = gpt_segment_chunks(client=client,
                                 prev_seg =prev_segment,
                                 prev_chunk=prev_chunk,
                                chunk=current_chunk,
                                dizer_prompt=segger_prompt,
                                            )
        try:
            print("res:",res)
            print("type",type(res))
           
            ddict = json.loads(res)

        except Exception as e:
            print(e)
    
            ddict = {'segment':'',
                      'questions':[]
                     }

        chunk_diarized =  {'chunk':{ 'text': current_chunk ,
                                        'segment': ddict['segment'],
                                        'questions':ddict['questions']
                                    }
                          }
        prev_segment = ddict['segment']
        prev_chunk = current_chunk[:1000]
        doc_meta[i]=chunk_diarized
    return doc_meta

def gpt_qa_digest_document_chunks(chunks,
                                digest_prompt,
                                  )->dict:
    client = get_openai_client()
    doc_meta = { }
    print("running gpt on the chunks, num chunks :", len(chunks))

    prev_chunk = None
    for i in range(len(chunks)):
        print("processing: ",i,'...') 
        current_chunk = chunks[i]
        res = gpt_qa_digest_chunks(client=client,
                                 prev_chunk=prev_chunk,
                                chunk=current_chunk,
                            dizer_prompt=digest_prompt,
                                            )
        

        chunk_diarized =  {'chunk':{ 'text': current_chunk ,
                                       'digest':res
                                    }
                          }
    
        prev_chunk = current_chunk[:1000]
        doc_meta[i]=chunk_diarized
    return doc_meta

def gpt_qa_digest_document_chain_chunks(chunks,
                                digest_prompt,
                                  )->dict:
    client = get_openai_client()
    doc_meta = { }
    print("running gpt on the chunks, num chunks :", len(chunks))

    prev_chunk_summary = None
    for i in range(len(chunks)-1):
        print("processing: ",i,'...') 
        print(chunks)
        current_chunk = chunks[i] + chunks[i+1]
        res = gpt_qa_digest_chunks(client=client,
                                 prev_chunk=prev_chunk_summary,
                                chunk=current_chunk,
                            dizer_prompt=digest_prompt,
                                            )
        

        chunk_diarized =  {'chunk':{ 'text': current_chunk ,
                                       'digest':res
                                    }
                          }
    
        prev_chunk_summary = res
        doc_meta[i]=chunk_diarized
    return doc_meta

def gpt_summarise_qa_digest(chunks,
                                digest_summary_prompt,
                                  )->dict:
    client = get_openai_client()
    sub_chunks = []
    sub_chunks.append(chunks[-1])

    sub_chunks.append(chunks[-2])

    print("running gpt on the chunks, num chunks :", len(chunks))
    concat_chunks = ' '.join(sub_chunks)

    res = gpt_summarise_qa_digest_doc(client=client,
                                        chunk=concat_chunks,
                                        dizer_prompt=digest_summary_prompt,
                                        )
    

    summary = {'qa_summary':res}

    return summary

    
def create_embeddings_from_chunk_doc( filename,
                                     text_column='chunk_text',
                                     gcs=False):
    # uses openai
    doc = _load_chunks_summary_doc(filename,gcs=gcs)
    embedded_doc = doc
    client = get_openai_client()
    for k,v in doc.items():
        print("embedding k",k)
        embedded_doc[k]['embedding'] = get_embedding(client,
                                                     embedded_doc[k][text_column]) 
    if not gcs:
        return _save_embedded_doc(embedded_doc,filename)
    else:
        print("GCS EMBEDDED upload",gcs)
        return upload_blob_to_gcs_bucket_by_filename(gcs_client=gcs_client,
                                              source_dir=EMBEDDING_DIR,
                                              source_filename=filename,
                                              data=embedded_doc)

from gpt_app.common.utils_dir import client as gcs_client
def create_text_meta_doc(ts_filename,
                        chunk_size=1000,
                        overlap= 100,
                        summariser_prompt=None,
                        sections=None,
                        gcs=False): # add gcs
    print("gcs",gcs)
    text = load_transcript_doc(ts_filename,gcs)
  
    words = count_words(text)
    char = len(text)
    print(words, char )
    if (char / chunk_size) > 15:
        chunk_size = int(chunk_size*1.45)
        print("new chunk size",chunk_size)
    chunks = split_document(text,chunk_size=chunk_size,overlap=overlap)
    print("num chunks", len(chunks))
    doc_sum_ = gpt_summarise_document_chunks(chunks,summariser_prompt=summariser_prompt,sections=sections) # uses openai 
    if not gcs:
        return save_summary_doc(doc_sum_,filename=ts_filename)
    else:
        print("GCS",gcs)
        print("fname",ts_filename)
        return upload_blob_to_gcs_bucket_by_filename(gcs_client=gcs_client,
                                              source_dir=SUMMARY_DIR,
                                              source_filename=ts_filename,
                                              format='json',
                                              data=doc_sum_)

def create_text_diarized_doc(ts_filename,
                        chunk_size=2000,
                        overlap= 100,
                        dizer_prompt=None,
                       ):

    text = load_transcript_doc(ts_filename)
  
    words = count_words(text)
    char = len(text)
    print(words, char )
    if (char / chunk_size) > 15:
        chunk_size = int(chunk_size*1.45)
        print("new chunk size",chunk_size)
    chunks = split_document(text,chunk_size=chunk_size,overlap=overlap)
    print("num chunks", len(chunks))
    doc_sum_ = gpt_diarize_document_chunks( chunks,dizer_prompt==dizer_prompt) # uses openai 
    return save_diarize_doc(doc_sum_,filename=ts_filename)

def create_text_segment_doc(ts_filename,
                        chunk_size=5000,
                        overlap= 100,
                        segger_prompt=None,
                        gcs=False
                       ):

    text = load_transcript_doc(ts_filename,gcs=gcs)
  
    words = count_words(text)
    char = len(text)
    print(words, char )
    if (char / chunk_size) > 15:
        chunk_size = int(chunk_size*1.45)
        print("new chunk size",chunk_size)
    chunks = split_document(text,chunk_size=chunk_size,overlap=overlap)
    print("num chunks", len(chunks))
    doc_sum_ = gpt_segment_document_chunks( chunks,segger_prompt=segger_prompt) # uses openai 
    if not gcs:
        return save_segment_doc(doc_sum_,filename=ts_filename)

    else:
        print("GCS",gcs)
        print("fname",ts_filename)
        return upload_blob_to_gcs_bucket_by_filename(gcs_client=gcs_client,
                                            source_dir=SEGMENT_DIR,
                                            source_filename=ts_filename,
                                            format='json',
                                            data=doc_sum_)


def get_summary_of_qa_doc(qa_digest):
    chunks  = [qa_digest[x]['chunk']['digest']  for x in qa_digest.keys()]
    prompt = f"""You are a helpful assistant to create the DETAILED SUMMARY a LONG DOCUMENT. \
                I have summarised many chunks. Based on the summaries, provide a comprehensive passage on the topics and subject of the \
              document to summarise finally. Keep it around 800 words."""
    
    qa_summary = gpt_summarise_qa_digest(chunks=chunks,digest_summary_prompt=prompt)
    return qa_summary 

def get_analyst_questions(file_name): # being used by /view/ directly
    text = _load_chunks_segment_doc(file_name)
    # print(text)
    qa = [text[x]['chunk']['questions']  for x in text.keys() if text[x]['chunk']['segment']=='QA']
    questions = [ ]

    # print("QA",questions)
    for x in qa:
        questions.extend(x)
    if not len(questions) >0:
        return { 'questions': []}

    s_prompt = "I will give you a list of questions extracted by an LLM from a transcript text. \
                Your job is to filter out the junk questions like 'can you hear me?' etc \
                declutter the questions. and return  \
                the list of questions in a json { question: '', } similar to the json given by me. "
    client = get_openai_client()
    res = gpt_filter_analyst_questions(client=client,text=questions,system_prompt=s_prompt)
    data = json.loads(res)
    # print("DATA",data)
    question_dict = { 'questions':data['questions'], 'raw_questions': questions}
   
    return question_dict

def get_qa_digest( ts_filename,
                    qa_digest_prompt=None,
                       ):
    digest_chain_prompt = "You are a helpful assistant to create the DETAILED SUMMARY a LONG QUARTERLY EARNINGS CONFERENCE CALL from text. \
                    The QA sections of the con-call will be provided in chunks.\
                    At the end there is a QnA where different fund houses representatives ask questions to the management \
                    I will provide you with the previous summary as context. Give increasingly detailed answer each time to enahnce the previous summary based on the new content. \
                    In case of no previous context it is the first chunk. Make a detailed digest that includes a summary of answers for the questions asked.  \
                    mentioned by management and concerns raised from the questions by the analyst \
                    . Avoid adding repetitive details and unnecessary opening texts like 'heres the answer..' etc. "
    
    text = _load_chunks_segment_doc(ts_filename)
    chunks  = [text[x]['chunk']['text']  for x in text.keys() if text[x]['chunk']['segment']=='QA']
    qdg = gpt_qa_digest_document_chain_chunks( chunks, digest_prompt=digest_chain_prompt) # uses openai 
    doc = {'qa_digest':qdg }
    summary = get_summary_of_qa_doc(qdg)
    doc['qa_summary'] =summary
    return doc


if __name__ =='__main__':
    filename = 'conc_earning_call_morepen.json'
    filename = 'Neuland_Laboratories_Ltd_Q4_FY2023-24_Earnings_Conference_Call.json'
    filename = 'Juan_Camilo_Avendano_and_Ankit_Gupta.json'
    def test_load_ts():
        tx = load_transcript_doc(filename)
  
        return count_words(tx)


    def test_summarise_doc_chunks():
        doc = load_transcript_doc(filename=filename)
        chunks = split_document(doc,chunk_size=3500,overlap=100)
        print("num chunks", len(chunks))
        doc_sum_ = gpt_summarise_document_chunks(chunks)
        return save_summary_doc(doc_sum_,filename=filename)

    def test_embed_chunk_summary_doc():
        return create_embeddings_from_chunk_doc(filename=filename)
    
    def test_service_create_summary_meta_doc():

        return create_text_meta_doc(ts_filename=filename,chunk_size=1000,summariser_prompt=summary_prmpt_interview,sections=sections_interview)
    # print(test_load_ts())
    # print(test_summarise_doc_chunks())
    # print(test_service_create_summary_meta_doc())
    print(test_embed_chunk_summary_doc())



