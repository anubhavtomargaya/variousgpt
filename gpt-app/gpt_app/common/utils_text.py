

from gpt_app.common.utils_openai import count_tokens
import hashlib

def count_words(text):
    words = text.split()
    return len(words)

def split_document(doc, chunk_size=1000, overlap=200):
    """input in # characters. Move back by 'overlap' characters for the next chunk"""
    if not doc:
        raise ValueError("doc not present") 
    chunks = []
    start = 0
    while start < len(doc):
        end = start + chunk_size
        chunks.append(doc[start:end])
        start = end - overlap 
    return chunks

def generate_hash_key(text):
    """Generates a hash key for a given text."""
    return hashlib.sha256(text.encode()).hexdigest()
def count_tokens_chunked(chunks):
    """ chunks are the output of split document """

    total_tokens = 0
    for i, chunk in enumerate(chunks):
        chunk_tokens = count_tokens(chunk)
        total_tokens += chunk_tokens
        print(f"Chunk {i+1} token count: {chunk_tokens}")

    print(f"Total number of tokens: {total_tokens}")

if __name__ == '__main__':pass