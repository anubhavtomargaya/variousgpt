

from gpt_app.common.supabase_handler import get_chunk_doc, update_doc_chunk
from gpt_app.common.utils_openai import get_openai_client, get_embedding


openai_client = get_openai_client()

def create_embedding_for_doc(file):
    chunks_dict = get_chunk_doc(file)
    for k,v in chunks_dict.items():
        chnk = v['chunk_text']
        if not chunks_dict[k]['chunk_embedding']:
            chunks_dict[k]['chunk_embedding'] = get_embedding(client=openai_client,
                                                          text=chnk)
            ures = update_doc_chunk(file=file,rich_chunks=chunks_dict)
            print(ures)
        else:
            pass
    return True

if __name__ == '__main__':
    f = 'Investors-call-transcript-for-Q4-FY-2023-24.pdf'
    def test_supabase_query():
        return get_chunk_doc(f)
    
    def test_create_embeddings():
        return create_embedding_for_doc(f)
    # print(test_supabase_query())
    print(test_create_embeddings())