
## working of pdf documents for extracting concall transcripts 

- make a bucket called `pdf-transcript`
- function to check what to do with the pdf i.e valid concall or not.
- triggered when new pdf lands in the bucket
- if its valid then :
        generate file name (appropriate format)
        insert into meta table (generate meta if needed)
        return in response the new file name and any addn meta.

- docker build -t gcr.io/gmailapi-test-361320/process_classify_pdf_metadata .
- docker push gcr.io/gmailapi-test-361320/process_classify_pdf_metadata

- gcloud functions deploy process_classify_pdf_metadata     --region=asia-southeast1     --runtime=python39     --trigger-http     --allow-unauthenticated     --source=.     --entry-point=validate_and_classify_pdf     --timeout=540s

- curl -X POST https://asia-southeast1-gmailapi-test-361320.cloudfunctions.net/pdf_transcript_processing_http -H "Content-Type: application/json" -d '{"name":""}'