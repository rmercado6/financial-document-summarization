# Financial Document Summarization

Leverage LLMs to summarize large financial documents such as annual and interim reports.

## data-crawler

The dataset for the document summarization is built with data for FTSE-ALL-SHARE shares from [hl.co.uk](hl.co.uk) and 
[annualreports.com](annualreports.com). The code for this is on the `data-crawler` module.

## data-insight

The `data-insight` module provides a script for generating an insight report from the outfile generated from the 
`data_crawler` module.

## Summarization

The `summarization` module provides the code needed to read documents from the dataset collected by the `data-crawler` 
module and code for using the `refine` method for document summarization with different LLMs such as _GPT_ and _Llama_.  


## Development Environment

### Venv
Create a virtual environment using `venv`.

Run the following command to create a virtual environment folder in the root of the repository.

```shell
python -m venv ./.venv
```

Then run the following commands to load the virtualenvironment and install dependencies.

```shell
source ./.venv/bin/activate
pip install -r requirements.txt
```

### Running the scripts

All the scripts under the `src` folder are programmed to behave as python modules, therefore it is necessary to let 
python know that when loading the scripts. Use the following commands at the root folder of the repository to run the 
different scripts.

```shell
# data-crawler
python -m src.data_crawler

# data-insight
python -m src.data_insight

# summarization
python -m src.summarization

```
