from handler_supabase import get_files_without_tags
from summary_mg import identify_transcript_tags, insert_tags_management_transcript
from utils_qa import load_ts_section_management


relevant_files = get_files_without_tags()
def process_intel_file(f):
    section = load_ts_section_management(f)
    s = identify_transcript_tags(section)
    if s:
        print("inserting")
        return insert_tags_management_transcript(f,s)
    else:
        print("not found")
        return None

for file in relevant_files:
    try:

        output = process_intel_file(file)
        print(output)
    except Exception as e:
        print('not able to process file ',file,e)
        pass