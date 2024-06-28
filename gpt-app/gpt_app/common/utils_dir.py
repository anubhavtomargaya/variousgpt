
import openai
from  gpt_app.common.dirs import * 
from pathlib import Path
import json 

def load_summary_embedded(file_name)->dict:
    file_path = Path(EMBEDDING_DIR,f"{Path(file_name).stem}.json")
    with open(file_path, 'r') as fr:
        return json.load(fr)
    
def save_summary(doc, file_name):
     file_path =  Path(SUMMARY_DIR,file_name)
     with open(file_path, 'w') as fw:
        return json.dump(doc,fw)
     
def check_ts_dir(file_name:Path):
    if not isinstance(file_name,Path):
        file_name = Path(file_name)
    file_stem = file_name.stem
    file = Path(TS_DIR,f"{file_stem}.json")
    return file.exists()

def check_summary_dir(file_name:Path):
    if not isinstance(file_name,Path):
        file_name = Path(file_name)
    file_stem = file_name.stem
    file = Path(SUMMARY_DIR,f"{file_stem}.json")
    return file.exists()

def check_diz_dir(file_name:Path):
    if not isinstance(file_name,Path):
        file_name = Path(file_name)
    file_stem = file_name.stem
    file = Path(DIARIZE_DIR,f"{file_stem}.json")
    return file.exists()
## transcript text
def load_transcript_doc(filename:Path)->str:
    if not isinstance(filename,Path):
        filename=Path(filename)
    path = Path(TS_DIR,f"{filename.stem}.json")
    with open(path,'r') as fr:
        transcript_dict = json.load(fr)
    return transcript_dict['text']

def update_transcript_doc(filename:Path,text:str)->str:
    if not isinstance(filename,Path):
        filename=Path(filename)

    print("file updating ")
    
    if not check_ts_dir(file_name=filename):
        raise Exception("No File by that name in transcripts: %s",filename.stem)
    
    path = Path(TS_DIR,f"{filename.stem}.json")
    with open(path,'r') as fr:
        transcript_dict = json.load(fr)
    if len(text) < (0.8* len(transcript_dict['text'])):
        raise Exception("Updated Text too less, please check!")
    print(text)
    transcript_dict['text']=text

    print(path.__str__())
    print(transcript_dict['text'])
    with open(path,'w') as fw:
        json.dump(transcript_dict,fw)
        return filename
       


def save_summary_doc(doc_summary_dict, filename):
    if not isinstance(filename,Path):
        filename = Path(filename)
    output_file = Path(SUMMARY_DIR,f'{filename.stem}.json')
    with open(output_file,'w') as fw:
        json.dump(doc_summary_dict,fw)
    return output_file

def save_diarize_doc(doc_summary_dict, filename):
    if not isinstance(filename,Path):
        filename = Path(filename)
    output_file = Path(DIARIZE_DIR,f'{filename.stem}.json')
    with open(output_file,'w') as fw:
        json.dump(doc_summary_dict,fw)
    return output_file

def _save_embedded_doc(embedded_doc_dict, filename):
    if not isinstance(filename,Path):
        filename = Path(filename)
    output_file = Path(EMBEDDING_DIR,f'{filename.stem}.json')
    with open(output_file,'w') as fw:
        json.dump(embedded_doc_dict,fw)
    return output_file


## mini-corpus-chunks-into-embedding


def _load_chunks_summary_doc(file_name)->dict:
    if not isinstance(file_name,Path):
        file_name = Path(file_name)
    file_path = Path(SUMMARY_DIR,f'{file_name.stem}.json')
    with open(file_path, 'r') as fr:
        return json.load(fr)
    
def _load_chunks_diarized_doc(file_name)->dict:
    if not isinstance(file_name,Path):
        file_name = Path(file_name)
    file_path = Path(DIARIZE_DIR,f'{file_name.stem}.json')
    with open(file_path, 'r') as fr:
        text =  json.load(fr)
    full_text= []
    for i in text:
        full_text.append(text[i]['diarize'])
    return ' '.join(full_text)

def list_embedding_dir():
    return [str(item.stem) for item in EMBEDDING_DIR.iterdir()]
## audio-text-processing

from  gpt_app.common.dirs import *


def save_transcript_srt(transcribed_srt,
                        file_name,
                        dir=PROCESSED_DIR):
    fpath = Path(dir,f'{file_name}.srt')
    print("saving subtitle  file to...", fpath)
    with open(fpath, 'w') as f:
        f.write(transcribed_srt)
    return True


def save_transcript_text_json(transcribed_text:openai.types.audio.transcription.Transcription, 
                      file_name,dir=PROCESSED_DIR):
    if not transcribed_text:
        raise ValueError("Missing arguments")
    fpath = Path(dir,f'{file_name}.json')
    print("saving json file to...", fpath)
    with open(fpath, 'w') as f:
        json.dump(transcribed_text.__dict__,f)
    return True



    
if __name__ == '__main__':
    def test_check_ts_dir():
        f = 'Avanti_Feeds_Ltd_Q4_FY2023-24_Earnings_Conference_Call.mp4'
        return check_ts_dir(f)
    
    print(test_check_ts_dir())