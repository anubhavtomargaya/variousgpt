

from utils_openai import get_embedding
from utils import get_openai_client
from utils_dir import load_summary_embedded

import numpy as np

client = get_openai_client()

def get_context_corpus(file_name):

    doc = load_summary_embedded(file_name)

    return doc

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
    prompt = "You are an expert analyst. Answer the following question based on the provided sections of a document.\n\n"
    
    for chunk in top_chunks:
        section = chunk['section']
        # summary = chunk['summary']
        texts = chunk['chunk_text']
        prompt += f"{section}: {texts}\n\n"
    
    prompt += f"Question: {question}\n"
    return prompt

from constants import DEFAULT_TEMPERATURE, DEFAULT_TOP_P


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
                                                    {"role": "user","content":prompt}],
                                                temperature=DEFAULT_TEMPERATURE,
                                                max_tokens=max_tokens,
                                                top_p=DEFAULT_TOP_P
                                            )
    answer = response.choices[0].message.content
    return  answer

from constants import DEFAULT_MODEL


def classify_question(client,question):
    classification_prompt = f"I will provide you with a prompt given by a user to an AI agent trained on a document. Use your intelligence to understand the intent of the user and classify the question as either : SPECIFIC or SUMMARY. return either of the two words in response. Heres the question as given by user: \n\nQuestion: {question}\n"

    
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

from utils_openai import count_tokens


def answer_question(doc, question):
    client = get_openai_client()
    classification = classify_question(client, question)
    print(classification)
    if classification == "summary":
        
        prompt = create_summary_prompt(doc)
        print(count_tokens(prompt))
    else:
        question_embedding = get_embedding(client,question)
        top_chunks = find_top_chunks(doc, question_embedding,top_n=3)
        summaries = [c['summary'] for c in top_chunks]
        texts = [c['chunk_text'] for c in top_chunks]
        # print(summaries)
        # print(texts)
        prompt = create_prompt(top_chunks, question)
        print(count_tokens(prompt))
    print("ANSWER:")
    answer = get_answer_from_gpt(client,prompt)
    return answer

if __name__=='__main__':
    filename =  'conc_earning_call_morepen.json'
    def test_answer_from_gpt():
        doc = get_context_corpus(file_name=filename)
        question = "What was the overall performance of the company in the last quarter?"
        
        return  answer_question(doc,question)
    
    print(test_answer_from_gpt())