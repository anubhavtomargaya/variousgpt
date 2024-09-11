MODEL_SEO = 'gpt-4o-mini'
from utils_em import get_openai_client,count_tokens,query_gpt                                                                                          
import json

openai_client = get_openai_client()




def top_questions(pdf_content, num_questions=10):
    """
    Generate top questions from a large PDF document for SEO optimization.
    
    :param pdf_content: The content of the PDF document as a string
    :param num_questions: Number of questions to generate (default: 10)
    :return: List of generated questions
    """
    prompt = f"""
    Analyze the following content from a PDF document and generate the top {num_questions} questions that could be asked about this content. 
    These questions should be optimized for SEO, meaning they should:
    1. Use relevant keywords and phrases that people might search for
    2. Be clear and concise
    3. Address key points or main ideas in the document
    4. Include a mix of informational and long-tail keyword questions
    5. Be phrased in a way that's likely to appear in search queries

    Here's the content:

    {pdf_content[:13000]}  # Limiting to first 3000 characters to avoid token limits

    Please provide the top {num_questions} SEO-optimized questions based on this content.
    Be direct and avoid using leadings phrases like here are the questions etc.
    """

    response = query_gpt(prompt)
    
    if response:
        # Split the response into individual questions
        questions = response.strip().split('\n')
        # Remove any numbering or extra spaces
        questions = [q.strip().lstrip('0123456789. ') for q in questions if q.strip()]
        return questions[:num_questions]  # Ensure we return only the requested number of questions
    else:
        return []

def generate_answer(pdf_content,
                        question):
    """
    Generate SEO-optimized content based on the top questions.
    
    :param pdf_content: The content of the PDF document as a string
    :return: Dictionary with questions as keys and generated content as values
    """
   
  


    prompt = f"""
    Based on the following question and the content from the PDF, generate a concise, SEO-optimized answer. 
    The answer should be informative, engaging, and incorporate relevant keywords naturally.

    Question: {question}

    PDF Content (excerpt):
    {pdf_content[:13000]} 

    Please provide an SEO-optimized answer to the question.
    Avoid 
    """

    answer = query_gpt(prompt)
    if answer:
        return answer
