from pathlib import Path


DATA_DIR = Path(Path(__file__).parent.resolve(), 'data')
PROCESSED_DIR = Path(DATA_DIR, 'processed')
CHOP_DIR = Path(PROCESSED_DIR, 'chopped')
TS_DIR = Path(PROCESSED_DIR, 'transcripts')