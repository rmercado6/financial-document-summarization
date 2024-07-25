from typing import Optional

from langchain_community.vectorstores import Chroma
from langchain_core.prompts import PromptTemplate
from langchain.chains.summarize import load_summarize_chain
from langchain_openai import OpenAIEmbeddings

# Prompts
initial_prompt_template: str = """Context information is below.
---------------------
{text}
---------------------
Given the context information and no prior knowledge, {task}:"""

refine_prompt_template: str = """The task is to {task}.
We have provided an initial summary: {existing_answer}
We have the opportunity to refine the existing summary
(only if needed) with some more context below.
------------
{text}
------------
Given the new context, refine the original summary to better fit the task.
You must provide a response, either the initial summary or refined summary."""


def refine(
        model,
        input_documents: list,
        return_intermediate_steps: bool = False,
        initial_prompt: str = initial_prompt_template,
        refine_prompt: str = refine_prompt_template,
        task: Optional[str] = 'make a summary',
        similarity_filter: bool = False
):
    """
    The function executes the langchain refine pipeline for summarising

    :arg model: the langauge model on which summarization would be done on
    :arg input_documents: list of the pages on which summarization would work on
    :arg return_intermediate_steps: if True, the intermediate steps will be included in the response,
    :arg initial_prompt: the prompt to use for the question step
    :arg refine_prompt:  the prompt to use for the refine steps
    :arg task: the main task, goal or question for the model to achieve through the pipeline
    :arg similarity_filter: whether to use a similarity filter

    :return: summarised output for the documents
    """
    # Do similarity filter
    if similarity_filter and task:
        db = Chroma.from_documents(input_documents, OpenAIEmbeddings())
        docs = db.similarity_search(task)
    else:
        docs = input_documents

    # Build prompts
    __question_prompt = PromptTemplate(
        template=initial_prompt.replace('{task}', task),
        input_variables=["text"]
    )
    __refine_prompt = PromptTemplate(
        template=refine_prompt.replace('{task}', task),
        input_variables=["text", "existing_answer"]
    )

    # Load the refine chain
    refine_chain = load_summarize_chain(
        model,
        chain_type="refine",
        question_prompt=__question_prompt,
        refine_prompt=__refine_prompt,
        return_intermediate_steps=return_intermediate_steps,
    )

    # Call the refine pipeline and return the output
    return refine_chain.invoke({"input_documents": docs})
