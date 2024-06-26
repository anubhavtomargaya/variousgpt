# 
import json
import requests
from pathlib import Path 
from openai import OpenAI
from constants import *

## setup.nb
def _load_config():

    with open(Path(Path(__file__).parent.resolve(),CONFIG_FILE)) as f:
        return json.load(f)

def get_openai_key():
    configs = _load_config()
    return configs[OPENAI_KEY]

def get_openai_client():
    client = OpenAI(
        timeout=50.0,
        api_key=get_openai_key())
    return client
    

def create_default_expert(system_content,
                          model=DEFAULT_MODEL):
    """ parameters available : model, system_content"""
    client = get_openai_client() 

    response = client.chat.completions.create(
                                                model=model,
                                                messages=[{
                                                            "role": "system",
                                                            "content":system_content
                                                        }],
                                                temperature=DEFAULT_TEMPERATURE,
                                                max_tokens=DEFAULT_MAX_TOKENS,
                                                top_p=DEFAULT_TOP_P
                                            )
    return response , client

def query_system_expert(user_input,
                    system_content = DEFAULT_SYSTEM_CONTENT,
                    model = DEFAULT_MODEL,
                    max_tokens = DEFAULT_MAX_TOKENS):
    
    client = get_openai_client() 

    response = client.chat.completions.create(
                                                model=model,
                                                messages=[{
                                                            "role": "system",
                                                            "content":system_content
                                                        },
                                                        {
                                                            "role": "user",
                                                            "content":user_input
                                                        }],
                                                temperature=DEFAULT_TEMPERATURE,
                                                max_tokens=max_tokens,
                                                top_p=DEFAULT_TOP_P
                                            )
    return response , client


def extract_message_choice(response ):
    # print("message rcvd:")
    # print(response.__dict__)
    usage = response.usage.__dict__
    print(usage)
    return response.choices[0].message.content
    
### jina.py

def read_web_content(url):
    jina_prefit = JINA_READER_PREFIX
    query_url = f"{jina_prefit}{url}"
    response = requests.get(query_url)
    return response

def read_search_results(text):
    jina_prefix =JINA_SEARCH_PREFIX
    query_url = f"{jina_prefix}{text}"
    response = requests.get(query_url)
    return response

def parse_jina_reader(mkdwn):pass
def parse_jina_search_results(mkdwn):pass

# import tiktoken

def estimate_cost(text):
  """
  This function estimates the cost (tokens) of a text prompt using tiktoken.

  Args:
      text: The text prompt for which to estimate the cost.

  Returns:
      An integer representing the estimated number of tokens in the prompt.
  """
  try:
    from tiktoken import Tokenizer
    tokenizer = Tokenizer()
    return tokenizer.tokenize(text)
  except ImportError:
    print("Tiktoken library not installed. Please install using 'pip install tiktoken'")
    return None
# whisper
from pydub import AudioSegment
def get_trx_cost(audio:AudioSegment):
   
    total_duration_milliseconds = len(audio)
    total_duration_seconds = total_duration_milliseconds / 1000
    total_duration_minutes = round(total_duration_seconds/60,2)
    rate = 0.006 #  / minute
    return round(total_duration_minutes * rate, 2)


# # Example usage
# text_prompt = "Write a poem about a cat"
# estimated_tokens = estimate_cost(text_prompt)

# if estimated_tokens:
#   print(f"Estimated cost (tokens) for prompt: {estimated_tokens}")

if __name__ == '__main__':
    
    def test_create_expert():
        content = DEFAULT_SYSTEM_CONTENT
        r, c = create_default_expert(content)
        print(r.choices)
        print(c)
    
    def test_expert_advice():
        user_input = "There are many fruits that were found on the recently discovered planet Goocrux. There are neoskizzles that grow there, which are purple and taste like candy. There are also loheckles, which are a grayish blue fruit and are very tart, a little bit like a lemon. Pounits are a bright green color and are more savory than sweet. There are also plenty of loopnovas which are a neon pink flavor and taste like cotton candy. Finally, there are fruits called glowls, which have a very sour and bitter taste which is acidic and caustic, and a pale orange tinge to them."
        nr , nc = query_system_expert(user_input)
        print(nc)
        msg = extract_message_choice(nr)
        return msg
   
    # print(test_create_expert())
    # print(test_expert_advice())