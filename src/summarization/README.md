# Summarization Module

This module allows to load a document from a jsonlines file and request summarization from multiple LLMs.

To run the script use the following commands at the root of the repository

```shell
python -m src.summarization                 # Models defaults to 'llama' 
python -m src.summarization --model gpt     # Uses 'ChatGPT' model. 
```

## Dependencies

Note that th script is currently dependant on having output file `data.jsonl` from the data-crawler in a folder 
`out/data-crawler` located at the root of the repository.
