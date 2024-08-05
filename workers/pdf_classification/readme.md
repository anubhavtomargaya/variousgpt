## working of pdf documents for extracting concall transcripts 

- make a bucket called `pdf-transcript`
- function to check what to do with the pdf i.e valid concall or not.
- triggered when new pdf lands in the bucket
- if its valid then :
        generate file name (appropriate format)
        insert into meta table (generate meta if needed)
        return in response the new file name and any addn meta.
