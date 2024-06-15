QA_RECORD_FILENAME = 'qa_chat_records.json'

class QARecord:
    def __init__(self,
                 filename,
                 question,
                 prompt_tokens,
                 answer) -> None:
        self.filename = filename
        self.question = question
        self.prompt_tokens = prompt_tokens
        self.answer = answer

from pathlib import Path
from typing import List
from dirs import QA_RECORD_DIR
import json 
qa_records_file = Path(QA_RECORD_DIR,QA_RECORD_FILENAME)
def load_qa_record()->List[QARecord]:
    with open(qa_records_file, 'r+') as f:
        try:
            existing_data = json.load(f)
        except json.JSONDecodeError:
            existing_data = []
    return existing_data

def save_qa_record(updated_data:List[QARecord]):
    with open(qa_records_file, 'w+') as f:
        json.dump(updated_data,f,indent=4)
    return True

if __name__=='__main__':
    def test_load_qa_record():
        return load_qa_record()
    
    print(test_load_qa_record())