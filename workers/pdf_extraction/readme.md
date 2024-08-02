## working of pdf documents for extracting concall transcripts 

- make a bucket called `pdf-transcript`
- function to check what to do with the pdf i.e valid concall or not.
- triggered when new pdf lands in the bucket
- if its valid then trigger the function to 
    - extract metadata - create entry in a table `pdf-transcripts`. get inserted id
    - extract transcript text as dictionary. use metadata if needed. update the entry using previous id
    -* check for existing in all cases
- returns the id to query the row