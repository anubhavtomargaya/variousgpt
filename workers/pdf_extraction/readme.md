## working of pdf documents for extracting concall transcripts 

- make a bucket called `pdf-transcript`
- function to check what to do with the pdf i.e valid concall or not.
- triggered when new pdf lands in the bucket
- if its valid then trigger the function to 
    - extract metadata - create entry in a table `pdf-transcripts`. get inserted id
    - extract transcript text as dictionary. use metadata if needed. update the entry using previous id
    -* check for existing in all cases
- returns the id to query the row

- docker build -t gcr.io/gmailapi-test-361320/gcr.io/gmailapi-test-361320/process_pdf_transcript_extraction .
- docker push gcr.io/gmailapi-test-361320/gcr.io/gmailapi-test-361320/process_pdf_transcript_extraction
- gcloud functions deploy process_pdf_extract_main_http     --region=asia-southeast1     --runtime=python39     --trigger-http     --allow-unauthenticated     --source=.     --entry-point=process_valid_pdf     --timeout=540s
- curl -X POST https://asia-southeast1-gmailapi-test-361320.cloudfunctions.net/process_pdf_extract_main_http -H 
"Content-Type: application/json" -d '{"name":""}'
