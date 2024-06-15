
from typing import List
from utils import _load_config
from constants import OPENAI_KEY
import tiktoken
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


def count_tokens(text, model="gpt-3.5-turbo"):
    encoding = tiktoken.encoding_for_model(model)
    tokens = encoding.encode(text)
    return len(tokens)
