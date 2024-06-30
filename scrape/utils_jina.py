## constants.py
JINA_READER_PREFIX  =  "https://r.jina.ai/"
JINA_SEARCH_PREFIX  =  "https://s.jina.ai/"
## jina.py
import requests

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

