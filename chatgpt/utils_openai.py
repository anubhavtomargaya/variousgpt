
from typing import List
from utils import _load_config
from constants import OPENAI_KEY
from openai import OpenAI
EMBEDDING_MODEL = "text-embedding-3-small"

def get_openai_key():
    configs = _load_config()
    return configs[OPENAI_KEY]

def get_embedding(client,text: str, model=EMBEDDING_MODEL, **kwargs) -> List[float]:
    # replace newlines, which can negatively affect performance.
    text = text.replace("\n", " ")

    response = client.embeddings.create(input=[text], model=model, **kwargs)

    return response.data[0].embedding

import tiktoken

def count_tokens(text, model="gpt-3.5-turbo"):
    # Load the appropriate encoding for the specified model
    encoding = tiktoken.encoding_for_model(model)
    
    # Encode the text using the model's tokenizer
    tokens = encoding.encode(text)
    
    # Return the number of tokens
    return len(tokens)