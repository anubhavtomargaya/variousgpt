from pathlib import Path


DATA_DIR = Path(Path(__file__).parent.resolve(), 'data')
RECORD_DIR = Path(DATA_DIR, 'records')
QA_RECORD_DIR = Path(RECORD_DIR, 'qa')
YOUTUBE_DIR = Path(DATA_DIR, 'youtube')
PROCESSED_DIR = Path(DATA_DIR, 'processed')
CHOP_DIR = Path(PROCESSED_DIR, 'chopped')
TS_DIR = Path(PROCESSED_DIR, 'transcripts')
SUMMARY_DIR = Path(TS_DIR, 'summary')
EMBEDDING_DIR = Path(SUMMARY_DIR, 'embeddings')