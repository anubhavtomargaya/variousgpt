 
from concall_question_over_knowledge import answer_question, get_context_corpus


filename =  'Neuland_Laboratories_Ltd_Q4_FY2023-24_Earnings_Conference_Call.json'

def test_answer_from_gpt_neuland():
    doc = get_context_corpus(file_name=filename)
    question = "What was the overall performance of the company in the last quarter?"
    question = "What will be their approximate revenue in coming two quarters comparing with YoY and this Quarter."
    question = "what measures the management is taking to keep the revenue and margins up in coming quarters?"
    question = "how does the management keep their employees motivated or follow work life balance? I want to understand the work culture in Morepen Lab."
    question = "what are the main products and revenue sources of this company?"

    question = "what were the key areas of performance growth in this quarter according to the management?"
    # question = "Summarise the analyst QnA of the call in around 600 words?"
    # question = "when is next tom cruise movie coming?"
    question = "what are the revenues and profit numbers of their competitors this quarter? If not available then just give me the competitor companies."
    question = "what does this company do? "

    question_prompt = f"the following documents will be provided from the transcript of the conference call of company {filename.split('.')[0].upper()}. If the name is misspelled somewhere in the following text, correct it yourself. "
    return  answer_question(doc,question,
                            file_name=filename,
                            question_prompt=question_prompt)

if __name__=='__main__':
    print(test_answer_from_gpt_neuland()) 