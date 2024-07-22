

from gpt_app.common.record_handler import load_qa_record,QARecord,save_qa_record
from gpt_app.common.utils_openai import get_openai_client,get_embedding,count_tokens
from gpt_app.common.session_manager import get_user_email
from gpt_app.common.utils_dir import load_summary_embedded
from gpt_app.common.supabase_handler import get_chunk_doc, insert_qa_entry
from gpt_app.common.constants import DEFAULT_TEMPERATURE, DEFAULT_TOP_P, DEFAULT_MODEL
from gpt_app.blueprints.gptube.tool_summarise import get_chained_summary
from gpt_app.blueprints.gptube.service_embed_text import get_summary_of_qa_doc
import numpy as np

client = get_openai_client()

def get_context_corpus(file_name):
    return load_summary_embedded(file_name)

def get_context_corpus_database(file):
    chunks_dict = get_chunk_doc(file)
    print("chunks dict")
    if not chunks_dict:
        raise Exception("file not found, %s,",file)
    print(chunks_dict.keys())
    x = [v.keys() for k,v in chunks_dict.items()]
    print(x)
    # print(chunks_dict)
    return chunks_dict

def find_top_chunks_database(chunk_dict, question_emb, top_n = 3):
    similarities = []
    for key, value in chunk_dict.items():
        chunk_embedding = value['chunk_embedding']
        if not chunk_embedding:
            raise Exception("embedding not found : %s",value)
        similarity = cosine_similarity(question_emb, chunk_embedding)
        similarities.append((key, similarity))
    
    similarities.sort(key=lambda x: x[1], reverse=True)
    top_chunks = [chunk_dict[k]['chunk_text'] for k, _ in similarities[:top_n]]
    print()
    return top_chunks


def embed_question(question):
    return get_embedding(client,question)

def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def find_top_chunks(doc:dict, question_embedding, top_n=3):
    similarities = []
    for key, value in doc.items():
        chunk_embedding = value['embedding']
        similarity = cosine_similarity(question_embedding, chunk_embedding)
        similarities.append((key, similarity))
    
    similarities.sort(key=lambda x: x[1], reverse=True)
    top_chunks = [doc[key] for key, _ in similarities[:top_n]]
    return top_chunks

def create_prompt(top_chunks, question):
    prompt = "Answer the following question based on the provided sections of a document.\n\n"
    
    for i,chunk in enumerate(top_chunks):
        # section = chunk['section']
        # summary = chunk['summary']
        texts = chunk
        prompt += f"{i}: {texts}\n\n"
    
    prompt += f"Question: {question}\n"
    return prompt

system_content =  "You are a helpful assistant."
def get_answer_from_gpt(client,
                        prompt,
                    system_content = system_content,
                    model = "gpt-3.5-turbo",
                    max_tokens = 150):
    
    response = client.chat.completions.create(
                                            model=model,
                                            messages=[
                                                    {"role": "system", "content":system_content},
                                                    {"role": "user","content":prompt}
                                                        ],
                                            temperature=DEFAULT_TEMPERATURE,
                                            max_tokens=max_tokens,
                                            top_p=DEFAULT_TOP_P
                                        )
    answer = response.choices[0].message.content
    return  answer


def classify_question(client,question):
    classification_prompt = f"I will provide you with a prompt given by a user to an AI agent trained on a document. \
                             Use your intelligence to understand the intent of the user and classify the question as either : SPECIFIC or SUMMARY. \
                             return either of the two words in response. Heres the question as given by user: \n\nQuestion: {question}\n"
    
    response = client.chat.completions.create(
                                            model=DEFAULT_MODEL,
                                            messages=[
                                                {"role": "system", "content":system_content},
                                                {"role": "user","content":classification_prompt}],
                                            temperature=DEFAULT_TEMPERATURE,
                                            max_tokens=300,
                                            top_p=DEFAULT_TOP_P
                                            )
    classification = response.choices[0].message.content.strip().lower()
    return classification

def create_summary_prompt(doc):
    print("creating summary prompt")
    prompt = "You are an expert analyst. Summarize the entire document based on the provided sections.\n\n"
    count = 0
    for key, chunk in doc.items():
        if count ==20:
            break
        else:
            section = chunk['section']
            summary = chunk['summary']
            prompt += f"{section}: {summary}\n\n"
            count +=1
    return prompt

def summarise_in_chunks(doc):
    print('doc')
    print(doc)

    qdg = get_chained_summary(doc)
    summary = get_summary_of_qa_doc(qdg)
    return summary['qa_summary']

## add save qa handling
def answer_question(doc,
                    question,
                    
                    question_prompt= '',
                    file_name = '',
                    _top_n=3):
    # records = load_qa_record()
    # client = get_openai_client()
    classification = classify_question(client, question)
    question_embedding = get_embedding(client,question)
    print(classification)
    if classification == "summary":
        
        # prompt = create_summary_prompt(doc)
        text_chunks = [ v['chunk_text'] for k,v in doc.items()]
        return summarise_in_chunks(text_chunks)
    else:
        top_chunks = find_top_chunks_database(doc, question_embedding,top_n=_top_n)
        prompt = create_prompt(top_chunks, question)
    
        aided_prompt = question_prompt + prompt
        tokens = count_tokens(aided_prompt)
        print(tokens)


        answer = get_answer_from_gpt(client,prompt=prompt,system_content=question_prompt)
        # record = QARecord(filename=file_name,
        #                   email=get_user_email(),
        #                   question=question,
        #                   prompt_tokens=tokens,
        #                   answer=answer)
        try:
                
            qa_document = QARecord(filename=file_name,
                            question=question,
                            prompt_tokens=tokens,
                            email=get_user_email(),
                            answer=answer
                            ) 

            print(qa_document.__dict__)
            qa_document._extra['classification'] = classification
            print(qa_document.__dict__)
            # records.append(record.__dict__)
            entry = insert_qa_entry(qa_document=qa_document.__dict__)
            # r = save_qa_record(records)
            print("record saved ", entry)
        except Exception as e:
            print("logging qa record failed")
            print(e)
        print("ANSWER:")
        return answer


question_prompt = " You will be provided with transcript chunks of a conference call. \
                    Followed by a question from an investor who is either invested in the  company or is looking to invest for mid to long term. Answer such that \
                    you are expert stocks analyst. All currency are in INDIAN RUPEES (INR). \
                    Answer without any starting phrases like '..here are the' etc. Only reply with the required information in concise but detailed manner \
                     \n  ORGANISATION : {organisation} \n FILENAME : {filename}"

def get_question_prompt(filename, org=None):
    return question_prompt.format(org,filename)

# organisation = 'Delhivery'
# filename =  'Delhivery_Ltd_Q4_FY2023-24_Earnings_Conference_Call.json'

if __name__=='__main__':
    # testing in files named test_rag_qa_...
    # doc = get_context_corpus(file_name=filename,)
    pass
    f = 'Investors-call-transcript-for-Q4-FY-2023-24.pdf'

    def test_embed_question(qtext):
        return embed_question(qtext)

    def test_corpus_load_from_db():
        return get_context_corpus_database(f)
    
    def test_top_chunks():
        chunks = get_context_corpus_database(f)
        q  = "How is the ebitda of this company?"
        emb = embed_question(q) 
        return find_top_chunks_database(chunk_dict=chunks,
                                        question_emb=emb,
                                        top_n=3)
    
    def test_answer_question():
        chunks = get_context_corpus_database(f)
        return answer_question(doc=chunks,question="What does this company do?")
    # print(test_corpus_load_from_db())
    # print(test_embed_question("How is the ebitda of this company?"))
    # print(test_top_chunks())
    print(test_answer_question())