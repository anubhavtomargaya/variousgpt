from generate_content import service_extract_seo_top_questions
import pandas as pd
data = pd.read_csv('pdf-transcripts_rows.csv')
files = list(data['file_name'].dropna().to_list())

def main():

    for file in files:
        print("running top qa for file:",file)
        r = service_extract_seo_top_questions(file_name=file)
        print(r)

    return True



if __name__=="__main__":
    print(main())
    
