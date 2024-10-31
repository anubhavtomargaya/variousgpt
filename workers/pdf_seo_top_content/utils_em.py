import json
from pathlib import Path
from typing import List
import openai
from openai import OpenAI
from datetime import datetime
from enum import Enum
import tiktoken 


BUCKET_NAME = 'gpt-app-data'
class tsFormats(Enum):
    JSON = 'json'
    SRT  = 'srt'
    TXT = 'txt'
## setup.nb
CONFIG_FILE='env.json'
def _load_config():
    with open(Path(Path(__file__).parent.resolve(),CONFIG_FILE)) as f:
        return json.load(f)
    
configs = _load_config()
SUPABASE_URL =configs['SUPABASE_URL']
SUPABASE_SERVICE_KEY = configs['SUPABASE_SERVICE_KEY']

def get_openai_key():
    configs = _load_config()
    return configs['OPENAI_KEY']

def get_openai_client():
    client = OpenAI(
        timeout=50.0,
        api_key=get_openai_key())
    return client
    
EMBEDDING_MODEL = "text-embedding-3-small"

def get_embedding(client,text: str, model=EMBEDDING_MODEL, **kwargs) -> List[float]:
    # replace newlines, which can negatively affect performance.
    text = text.replace("\n", " ")

    response = client.embeddings.create(input=[text], model=model, **kwargs)

    return response.data[0].embedding


def count_tokens(text, model="gpt-3.5-turbo"):
    encoding = tiktoken.encoding_for_model(model)
    tokens = encoding.encode(text)
    return len(tokens)

def split_document(doc, chunk_size=1000, overlap=200):
    """input in # characters. Move back by 'overlap' characters for the next chunk"""
    if not doc:
        raise ValueError("doc not present") 
    chunks = []
    start = 0
    while start < len(doc):
        print("chunking")
        end = start + chunk_size
        chunks.append(doc[start:end])
        start = end - overlap 
    return chunks


def create_seo_content_doc_for_file(filename,
                                    top_questions:dict,
                                    addn_content:dict,
                                
                                    meta:dict={}):
    """ make the dict in first stage of storing content doc
    """
    

    doc = {'file_name':filename,
           'top_qa':top_questions, #dict
           'addn_content':addn_content, #dict 
           'metadata':meta # dict 
           }
   
    return doc

def upload_blob_to_gcs_bucket_by_filename(gcs_client,
                            source_filepath:Path,
                            dest_dir:Path=None,
                            bucket=BUCKET_NAME,
                            format=None,
                            data=None
                            
                              ):
    bucket = gcs_client.bucket(bucket)
    src_file = Path(source_filepath).stem
    print("FILNEAME",src_file )
    destination_blob_name = _make_file_path(dest_dir,
                                            src_file,
                                            format=format,
                                            local=False)
    print("DESTBLOB",destination_blob_name)
    blob = bucket.blob(destination_blob_name)
    
    if blob.exists():
        return destination_blob_name
    if not data:
        upload = blob.upload_from_filename(Path(source_filepath).__str__())
    else:
        upload = blob.upload_from_string(str(data))
    print("uploaded:",upload)
    print("gcs name,",destination_blob_name)
    exists = blob.exists()
    print(f"Upload successful: {exists}")
    return destination_blob_name
                                                                                              

openai_client = get_openai_client()
import json
def query_gpt(prompt,
              model="gpt-4o-mini",
              response_format='text',
                temperature=0.1,
              max_tokens=15000):

    """
    Query GPT with support for different response formats
    
    Args:
        prompt (str): The input prompt
        model (str): The model to use
        response_format (str): Desired response format - 'text', 'json', or 'structured'
    
    Returns:
        The formatted response or False if error occurs
    """
    tokens = count_tokens(text=prompt, model=model)
    print("tokens", tokens)
    
    # Adjust system message based on response format
    system_message = get_system_message(response_format)
    
    try:
        # Add format instructions to prompt if needed
        formatted_prompt = format_prompt(prompt, response_format)
        
        # Configure response format parameter
        response_params = {}
        if response_format == 'json':
            response_params['response_format'] = {"type": "json_object"}
        
        response = openai_client.chat.completions.create(
            model=model,
            temperature=temperature,  # Low temperature for consistency
            max_tokens=max_tokens,    # Control response length
            top_p=0.1,               # Lower top_p for more focused responses
            frequency_penalty=0.2,    # Slight penalty for repetition
            presence_penalty=0.1,   
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": formatted_prompt}
            ],
            **response_params
        )
        
        result = response.choices[0].message.content
        
        # Process the result based on response format
        if response_format == 'json':
            try:
                return json.loads(result)
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON response: {str(e)}")
                print(f"Raw response: {result[:200]}...")
                return False
        
        elif response_format == 'structured':
            # For structured format, attempt to parse as JSON first
            try:
                return json.loads(result)
            except json.JSONDecodeError:
                # If not valid JSON, return as is
                return result
        
        return result
        
    except Exception as e:
        print(f"Error in query_gpt: {str(e)}")
        if hasattr(response, 'choices') and len(response.choices) > 0:
            print(f"Raw response content: {response.choices[0].message.content[:200]}...")
        return False

def get_system_message(response_format):
    """
    Get appropriate system message based on response format
    """
    base_message = "You are a helpful analyst."
    
    if response_format == 'json':
        return base_message + " Always respond with valid JSON."
    elif response_format == 'structured':
        return base_message + " Provide structured, detailed responses."
    return base_message

def format_prompt(prompt, response_format):
    """
    Format the prompt based on desired response format
    """
    if response_format == 'json':
        # Add explicit JSON formatting instruction if not already present
        if not any(keyword in prompt.lower() for keyword in ['json', 'format']):
            prompt += "\nProvide the response in JSON format."
    
    elif response_format == 'structured':
        if not 'structure' in prompt.lower():
            prompt += "\nProvide a well-structured response."
    
    return prompt


def _make_file_path(direcotry:Path,
                    file_name:Path,
                    format:str=None,
                    local=True):
    if not format:
        format = Path(file_name).as_posix().split('.')[-1]
    file_ = f"{Path(file_name).stem}.{format}"
    print("making file path",file_)
    if local:
        return Path(direcotry,file_)
    else:
        parts = direcotry.parts
        if not "data" in parts:
            raise ValueError("DATA DIR not found in path")
        
        data_index = parts.index("data")
        after_data = "/".join(parts[data_index:])

        return f"{after_data}/{file_}"
