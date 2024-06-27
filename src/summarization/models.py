import os

from langchain_community.llms import OpenAI
from langchain_huggingface import HuggingFaceEndpoint


def load_huggingface_model(repo_id):
    """
    load open source models from huggingface

    Args:
        repo_id (str): the model repo which is to be loaded
    Returns:
        llm: the langauge model on which queries/summarsation would be done on
    """
    huggingface_key = os.environ['HUGGINGFACEHUB_API_TOKEN']
    llm = HuggingFaceEndpoint(
        huggingfacehub_api_token=huggingface_key,
        repo_id=repo_id,
        temperature=0.8,
        max_new_tokens=200
    )
    return llm


def load_openai_model(model_name):
    """
    load openai models

    Args:
        model_name (str): the model to be used from openai
    Returns:
        llm: the langauge model on which queries/summarsation would be done on
    """
    llm = OpenAI(
        model_name=model_name,
        openai_api_key=os.environ["OPENAI_API_KEY"]
    )
    return llm


def load_model(model_name):
    if model_name == 'gpt':
        return load_openai_model("gpt-3.5-turbo-instruct")
    else:
        # model_name = "meta-llama/Meta-Llama-3-8B-Instruct"
        return load_huggingface_model("mistralai/Mistral-7B-Instruct-v0.3")
