import requests

def build_audio_transcribe_request(audio_filename):
  """
  This function builds a POST request to transcribe audio using the provided filename.

  Args:
      audio_filename (str): The name of the audio file to transcribe.

  Returns:
      requests.Response: The response object from the API call.
  """
  url = "https://asia-southeast1-gmailapi-test-361320.cloudfunctions.net/audio_transcribe_http"
  headers = {"Content-Type": "application/json"}
  data = {"name": audio_filename}

  response = requests.post(url, headers=headers, json=data)
  return response

if __name__=='__main__':
    sp_file = 'World_Exclusive!_CZINGER_21C_FIRST_DRIVE_2m_1233bhp_3D-printed_hypercar__Top_Gear.webm'
    def trigger_sample_worker():
        print("STARTING TRANSCRIPTION...")
        response = build_audio_transcribe_request(sp_file)

        
        if response.status_code == 200:
            print(response.__dict__)
            print("Audio transcription successful!")
        else:
            print(f"Error transcribing audio: {response.status_code}")
    
    trigger_sample_worker()