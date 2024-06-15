

from save_qa import load_qa_record,QARecord,save_qa_record
from utils_openai import get_embedding,count_tokens
from utils import get_openai_client
from utils_dir import load_summary_embedded
from constants import DEFAULT_TEMPERATURE, DEFAULT_TOP_P, DEFAULT_MODEL

import numpy as np

client = get_openai_client()

def get_context_corpus(file_name):
    return load_summary_embedded(file_name)

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
    
    for chunk in top_chunks:
        section = chunk['section']
        # summary = chunk['summary']
        texts = chunk['chunk_text']
        prompt += f"{section}: {texts}\n\n"
    
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
## add save qa handling
def answer_question(doc,
                    question,
                    question_prompt= '',
                    file_name = '',
                    _top_n=3):
    records = load_qa_record()
    client = get_openai_client()
    classification = classify_question(client, question)
    print(classification)
    if classification == "summary":
        
        prompt = create_summary_prompt(doc)
       
    else:
        question_embedding = get_embedding(client,question)
        top_chunks = find_top_chunks(doc, question_embedding,top_n=_top_n)
        # summaries = [c['summary'] for c in top_chunks]
        # texts = [c['chunk_text'] for c in top_chunks]
        # print(summaries)
        # print(texts)
        prompt = create_prompt(top_chunks, question)
    
    aided_prompt = question_prompt + prompt
    tokens = count_tokens(aided_prompt)
    print(tokens)


    answer = get_answer_from_gpt(client,prompt=prompt,system_content=question_prompt)
    record = QARecord(filename=file_name,
                      question=question,prompt_tokens=tokens,answer=answer)
    record._extra['classification'] = classification
    records.append(record.__dict__)
    r = save_qa_record(records)
    print("record saved ", r)
    print("ANSWER:")
    return answer

if __name__=='__main__':
    # testing in files named test_rag_qa_...
    pass