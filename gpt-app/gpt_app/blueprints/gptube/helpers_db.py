from typing import Optional
from pydantic import BaseModel

class Chunks(BaseModel):
    chunk_text:str
    chunk_embedding:Optional[list]
    chunk_meta:dict={}

class RAGDoc(BaseModel):
    file_name:str
    chunks:Chunks
    metadata:dict


def create_doc_for_file(filename, chunks:list,e='pdf', meta:dict={}):
    """ make the dict in first stage of storing doc (towards common format)
    """
    meta['chunks_num']= len(chunks)
    c = {n:{
        'chunk_text':v,
        'chunk_embedding':None,
        'chunk_meta':{ }} for n,v in enumerate(chunks)}

    doc = {'file_name':filename.split('.')[0],
           'chunks':c,
           'extn':e,
           'metadata':meta
           }
   
    return doc