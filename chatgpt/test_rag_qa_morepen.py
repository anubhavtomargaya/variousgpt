
from concall_question_over_knowledge import answer_question, get_context_corpus


filename =  'conc_earning_call_morepen.json'

def test_answer_from_gpt():
    doc = get_context_corpus(file_name=filename)
    question = "What was the overall performance of the company in the last quarter?"
    # question = "What will be their approximate revenue in coming two quarters comparing with YoY and this Quarter."
    # question = "what measures the management is taking to keep the revenue and margins up in coming quarters?"
    # question = "how does the management keep their employees motivated or follow work life balance? I want to understand the work culture in Morepen Lab."
    # question = "what are the main products and revenue sources of this company?"
    # question = "what are the APIs they referred to? do they make software as well!! ?"
    # question = "when is next tom cruise movie coming?"
    # question = "what are the revenues and profit numbers of their competitors this quarter? If not available then just give me the competitor companies."
    # question = "What is this Roche? was it discussed in the call?"
    
    return  answer_question(doc,question,file_name=filename)

print(test_answer_from_gpt()) 