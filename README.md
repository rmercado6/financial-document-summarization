# Financial Document Summarization

Leverage LLMs to summarize large financial documents such as annual and interim reports.


## Projects

### data-crawler
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)

The dataset for the document summarization is built with data for FTSE-ALL-SHARE shares from [hl.co.uk](hl.co.uk) and 
[annualreports.com](annualreports.com). The information is collected in markdown format to facilitate the usage of 
documents with LLMs while keeping information such as headers.

The code for this is on the `src.data_crawler` module.


### data-insight
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)

The `src.data_insight` module provides a script for generating an insight report from the outfile generated from the 
`data_crawler` module.


### Summarization
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)

The `src.summarization` module provides the code needed to read documents from the dataset collected by the 
`src.data-crawler` module and code for using the `refine` method for document summarization with different LLMs such as 
_GPT_, _Llama_, and __Mistral__. 


### PDF Converter
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)

The `src.pdf_converter` module provides the code por converting any given pdf file into the required format for 
interaction with other systems in the repo. 


### Experiment UI
[![Docker](https://badgen.net/badge/icon/docker?icon=docker&label)](https://https://docker.com/)

The `Experiment UI` project is a fullstack web application that allows to query the collected data from the 
`src.data_crawler` module. 

The application allows to view a list of collected documents and preview them documents on rendered markdown 
or raw text to understand the input that the LLMs will be receiving. 
It provides a form for querying the LLMs about the documents with both `refine` and `mapreduce` pipelines.
Finally, the application allows to keep track of experiments by storing the LLMs' responses and displaying them in an 
interface designed to view all the steps and compare the input for each to the output. It provides a section for adding 
comments to the experiments to facilitate the tracking o the analysis done to each of the experiments. 

#### Backend
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)

Fast API application. Provides access to stored information scraped through the `src.data_crawler` module. 
It is also in charge of querying LLMs' and keeping track of their responses and any comments the user may add.

> The application currently uses only `jsonl` files for storage instead of databases. The ideal situation would be to
> implement a database system to store documents, queries and responses, and comments.


#### Frontend
[![made-with-javascript](https://img.shields.io/badge/Made%20with-JavaScript-1f425f.svg)](https://www.javascript.com)

Vue3 application. Front end application containing all the user interface. Allows user to interact with the API.


## Development Environment


### Python Modules

#### Venv
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

#### Running the python modules

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

# pdf_converter
python -m src.pdf_converter args

```

##### pdf converter arguments
The `pdf_converter` requires some arguments as the information stored from file should be tied to a company.

The arguments the module require are: 
```text
usage: __main__.py [-h] [--output OUTPUT] [-r] path title ticker document_type year

positional arguments:
  path             path of the file to be converted.
  title            title of the company to whom the file refers to.
  ticker           ticker of the company to whom the file refers to.
  document_type    document type of the file to be converted.
  year             year in which the document was published or to which it refers to.

options:
  -h, --help       show this help message and exit
  --output OUTPUT  The output path in where to place the output data.jsonl file.
  -r, --remote     Whether or not the path belongs to a remote file url.

```


### Web Application

#### Docker Compose
The web application could be started on it's own by running the _fast-api_ application on a _gunicorn_ server and the 
_Vue3_ application using _vite_ and _node_, however, to facilitate the process of setting things up, _Docker_ container 
have been setup. Using `docker-compose` the process to setup the environment is as easy as running a single command.

To run the application environment with docker compose run the following command on the root of the repository:

```shell
docker compose -f ./src/experiment_ui/docker-compose.yaml -p experiment-ui up -d --build
```
