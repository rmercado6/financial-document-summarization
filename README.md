# Financial Document Summarization

Leverage LLMs to summarize large financial documents such as annual and interim reports.

## data-crawler

The dataset for the document summarization is built with data for FTSE-ALL-SHARE shares frm [hl.co.uk](hl.co.uk) and 
[annualreports.com](annualreports.com). The code for this is on the `data-crawler` module.

## data-insight

The `data-insight` module provides a script for generating an insight report from the outfile generated from the 
`data_crawler` module.

## Summarization

The `summarization` module provides the code needed to read documents from the dataset collected by the `data-crawler` 
module and code for using the `refine` method for document summarization with different LLMs such as _GPT_ and _Llama_.  
