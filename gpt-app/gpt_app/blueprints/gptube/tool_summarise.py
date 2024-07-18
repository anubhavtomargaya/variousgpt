from gpt_app.blueprints.gptube.service_embed_text import gpt_qa_digest_document_chain_chunks

def get_chained_summary( chunks,
                       ):
    digest_chain_prompt = """
        You are a helpful assistant to create the DETAILED SUMMARY a LONG DOCUMENT. \
        You will be given a chunk of TEXT and \
        I will provide you with the previous TEXT CHUNK summary as context. Give increasingly detailed answer each time to enahnce the previous summary based on the new content. \
        In case of no previous context it is the first chunk. \
        .Avoid adding repetitive details and unnecessary opening texts like 'heres the answer..' etc. """
    

  
    qdg = gpt_qa_digest_document_chain_chunks( chunks, digest_prompt=digest_chain_prompt) # uses openai 
    doc = {'qa_digest':qdg }
    # summary = get_summary_of_qa_doc(qdg)
    # doc['qa_summary'] =summary
    print("summary chained")
    print(doc)
    return qdg
