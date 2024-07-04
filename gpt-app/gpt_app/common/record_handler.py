from datetime import datetime
from pathlib import Path
from typing import List
import json 

from .enums import Experiments
from .dirs import QA_RECORD_DIR

QA_RECORD_FILENAME = 'qa_chat_records.json'
QA_RECORD_FILE = Path(QA_RECORD_DIR,QA_RECORD_FILENAME)


class QARecord:
    def __init__(self,
                 
                 filename,
                 question,
                 prompt_tokens,
                 answer,
                 experiment=Experiments.CURRENT.value,
                 timestamp=None,
                 email=None,
                 google_id=None,
                 session_id=None,
                 client_id = None,
                 _extra:dict={},
                 ) -> None:
        self.timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        self.filename = filename
        self.question = question
        self.prompt_tokens = prompt_tokens
        self.answer = answer
        self._extra = _extra
        self.email = email
        self.session_id = session_id
        self.experiment = experiment


def load_qa_record()->List[QARecord]:
    with open(QA_RECORD_FILE, 'r+') as f:
        try:
            existing_data = json.load(f)
        except json.JSONDecodeError:
            existing_data = []
    return existing_data

def save_qa_record(updated_data:List[QARecord]):
    with open(QA_RECORD_FILE, 'w+') as f:
        json.dump(updated_data,f,indent=4)
    return True


if __name__=='__main__':
    def test_load_qa_record():
        return load_qa_record()
    
    def update_record_schema():
        data =load_qa_record()
        new_schema_data = [ QARecord(**x).__dict__ for x in data]

        # return new_schema_data
        return save_qa_record(new_schema_data)

    # print(test_load_qa_record())
    print(update_record_schema())