# Data crawler

This module allow to scrape data for the FTSE-ALL-SHARE shares from [hl.co.uk](hl.co.uk) and 
[annualreports.com](annualreports.com). 

## Output

The output of the script is a jsonlines file `data.jsonl` placed in `out/data-crawler` which is located at the root of 
the repository.

Each line of this file contains the information of each scraped files. This information follows this structure:

```json lines
{"title": "doc1", "ticker": "SPA", "year": "2013", "document_type": "annual_report", "doc": "doc content"}
```

| property      | description                                                      |
|---------------|------------------------------------------------------------------|
| title         | Name of the company                                              |
| ticker        | Ticker of the company                                            |
| year          | Year the document was published                                  |
| document_type | Type of the document                                             |
| doc           | The scraped content. PDF content processed to extract text only. |
