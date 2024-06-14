
from dirs import * 
from pathlib import Path
import json 

def load_summary_embedded(file_name)->dict:
    file_path = Path(EMBEDDING_DIR,file_name)
    with open(file_path, 'r') as fr:
        return json.load(fr)
    
def save_summary(doc, file_name):
     file_path =  Path(SUMMARY_DIR,file_name)
     with open(file_path, 'w') as fw:
        return json.dump(doc,fw)
