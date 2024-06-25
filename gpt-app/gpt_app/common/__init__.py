import logging
from logging.handlers import RotatingFileHandler
import sys 
# LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_FORMAT = '%(asctime)s - %(name)s - %(funcName)s - %(levelname)s - %(message)s' #FUNC
formatter = logging.Formatter(LOG_FORMAT)


# fh = logging.FileHandler('test.log')
# fh.setLevel(logging.INFO)
# fh.setFormatter(formatter)

# file_handler = RotatingFileHandler('info.log', maxBytes=1024 * 1024 * 100, backupCount=20)
# file_handler.setLevel(logging.INFO)

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(logging.Formatter(LOG_FORMAT))


from .dirs import *
import os
print(DATA_DIR)
for directory in [DATA_DIR, VIDEO_DIR, RECORD_DIR, QA_RECORD_DIR, YOUTUBE_DIR, PROCESSED_DIR, CHOP_DIR, TS_DIR, SUMMARY_DIR, EMBEDDING_DIR]:
    try:
        os.makedirs(directory, exist_ok=True)  # Avoids errors if directory already exists
        print(f"Directory created: {directory}")
    except OSError as e:
        print(f"Error creating directory {directory}: {e}")



def create_qa_records_file(file= QA_RECORD_FILE):
    try:
        with open(file, "x") as f:
            f.write('')
    except FileExistsError:
        print("File already exists.",file)
    return True

        
def create_yt_index(file=YOUTUBE_META_FILE):
    try:
        with open(file, "x") as f:
            f.write('')
    except FileExistsError:
        print("File already exists.",file)
    
    return True

create_yt_index()
create_qa_records_file()