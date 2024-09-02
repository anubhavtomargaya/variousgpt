## running all workers 

import requests

def run_classifier(name):
    url = "https://asia-southeast1-gmailapi-test-361320.cloudfunctions.net/gen1_classify_upload_pdf"
    headers = {"Content-Type": "application/json"}
    data = {"name": name}

    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        return response.json()  # Assuming the response is in JSON format
    else:
        return {"error": response.status_code, "message": response.text}



def run_chunk_embed_pdf(name):
    url = "https://asia-southeast1-gmailapi-test-361320.cloudfunctions.net/pdf_chunk_embed_http"
    headers = {"Content-Type": "application/json"}
    data = {"name": name}

    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        return response.json()  # Assuming the response is in JSON format
    else:
        return {"error": response.status_code, "message": response.text}

def run_qa_mg_intel(filename): # stage 1 intel
    url = "https://asia-southeast1-gmailapi-test-361320.cloudfunctions.net/process_qa_mg_intel_http"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "name": filename
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        return response.json() 
    else:
        print("msg",{"error": f"Request failed with status code {response.status_code}"})
        return False
    


def run_extract_pdf_transcript(name):
    url = "https://asia-southeast1-gmailapi-test-361320.cloudfunctions.net/process_pdf_transcript_intel"
    headers = {"Content-Type": "application/json"}
    data = {"name": name}

    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        return response.json()  # Assuming the response is in JSON format
    else:
        return {"error": response.status_code, "message": response.text}



if __name__=='__main__':
    f = 'fy-2025_q1_earnings_call_transcript_ghcl_500171.pdf'
    print(run_chunk_embed_pdf(f ))