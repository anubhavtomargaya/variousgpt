 
from concall_question_over_knowledge import answer_question, get_context_corpus


filename =  'Juan_Camilo_Avendano_and_Ankit_Gupta.json'

def test_answer_from_gpt_scispace():
    doc = get_context_corpus(file_name=filename)
    question = "what is this call about"
    question = "what are the pain points mentioned by the user ?"
    question = "what are the action items i can add in my next quarter's roadmap for the copilot based on the users response?"

    
    question_prompt = f" You will be provided with transcript chunks of an interview call between a Product manger and a customer \
                            the user is a churned out user and the PM seeks to gains some insights into the reasons."
    return  answer_question(doc,question,
                            file_name=filename,
                            question_prompt=question_prompt,
                            _top_n=5)

if __name__=='__main__':
    print(test_answer_from_gpt_scispace()) 