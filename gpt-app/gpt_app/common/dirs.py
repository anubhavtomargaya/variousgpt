import os
from pathlib import Path


DATA_DIR = Path(Path(__file__).parent.parent.resolve(), 'data')
VIDEO_DIR = Path(DATA_DIR, 'video')

YOUTUBE_DIR = Path(DATA_DIR, 'youtube')
TS_DIR = Path(DATA_DIR, 'transcripts')
PROCESSED_DIR = Path(DATA_DIR, 'processed')
CHOP_DIR = Path(PROCESSED_DIR, 'chopped')
SUMMARY_DIR = Path(TS_DIR, 'summary')
EMBEDDING_DIR = Path(SUMMARY_DIR, 'embeddings')

RECORD_DIR = Path(DATA_DIR, 'records')
QA_RECORD_DIR = Path(RECORD_DIR, 'qa') 
if __name__=='__main__':
    print(DATA_DIR)
    for directory in [DATA_DIR, VIDEO_DIR, RECORD_DIR, QA_RECORD_DIR, YOUTUBE_DIR, PROCESSED_DIR, CHOP_DIR, TS_DIR, SUMMARY_DIR, EMBEDDING_DIR]:
        try:
            os.makedirs(directory, exist_ok=True)  # Avoids errors if directory already exists
            print(f"Directory created: {directory}")
        except OSError as e:
            print(f"Error creating directory {directory}: {e}")