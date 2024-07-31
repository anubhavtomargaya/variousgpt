# working
1. take audio filename as input via http POST 
2. downloads audio file from bucket `youtube-bucket-audio`
    opens as segment using `pydub`
3. chops audio, exports as path and returns generator
4. transcribes segment in loop and appends in a dictionary 
5. saves the dict as json by the same name as input filename in `/tmp` dir
6. uploads the file to bucket `gpt-app-data` in TS_DIR and returns path 

``` 
gcloud functions deploy audio_transcribe_http     --region=asia-southeast1     --runtime=python39     --trigger-http     --allow-unauthenticated     --source=.     --entry-point=transcribe_audio_file  --memory=2048MB  --timeout=540s
```