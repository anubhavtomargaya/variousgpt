import os
from pathlib import Path


DATA_DIR = Path(Path(__file__).parent.parent.resolve(), 'data')
VIDEO_DIR = Path(DATA_DIR, 'video')

YOUTUBE_DIR = Path(DATA_DIR, 'youtube')
TS_DIR = Path(DATA_DIR, 'transcripts')
PROCESSED_DIR = Path(DATA_DIR, 'processed')
CHOP_DIR = Path(PROCESSED_DIR, 'chopped')
SUMMARY_DIR = Path(TS_DIR, 'summary')
DIGEST_DIR = Path(TS_DIR, 'digest')
DIARIZE_DIR = Path(TS_DIR, 'diarized')
SEGMENT_DIR = Path(TS_DIR, 'segments')
QUESTIONS_DIR = Path(SEGMENT_DIR, 'questions')
EMBEDDING_DIR = Path(SUMMARY_DIR, 'embeddings')

RECORD_DIR = Path(DATA_DIR, 'records')
QA_RECORD_DIR = Path(RECORD_DIR, 'qa') 

#FILES
YOUTUBE_META_FILE = Path(YOUTUBE_DIR,'index.json')
QA_RECORD_FILENAME = 'qa_chat_records.json'
QA_RECORD_FILE = Path(QA_RECORD_DIR,QA_RECORD_FILENAME)
if __name__=='__main__':
    print(DATA_DIR)
    for directory in [DATA_DIR, VIDEO_DIR, RECORD_DIR, QA_RECORD_DIR, YOUTUBE_DIR, PROCESSED_DIR, CHOP_DIR, TS_DIR, SUMMARY_DIR, EMBEDDING_DIR]:
        try:
            os.makedirs(directory, exist_ok=True)  # Avoids errors if directory already exists
            print(f"Directory created: {directory}")
        except OSError as e:
            print(f"Error creating directory {directory}: {e}")