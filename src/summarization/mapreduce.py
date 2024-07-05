from langchain_core.prompts import PromptTemplate
from langchain.chains.summarize import load_summarize_chain


# Refine prompts
map_prompt_template = """
                      Write a summary of this chunk of text that includes the main points and any important details.
                      {text}
                      """

combine_prompt_template = """
                      Write a concise summary of the following text delimited by triple backquotes.
                      Return your response in bullet points which covers the key points of the text.
                      ```{text}```
                      BULLET POINT SUMMARY:
                      """


def map_reduce(model, input_documents: list, return_intermediate_steps: bool = False):
    """
    The function executes the langchain refine pipeline for summarising

    :arg model: the langauge model on which summarization would be done on
    :arg input_documents: list of the pages on which summarization would work on
    :arg return_intermediate_steps: if True, the intermediate steps will be included in the response

    :return summarised output for the documents
    """
    map_prompt = PromptTemplate(template=map_prompt_template, input_variables=["text"])
    combine_prompt = PromptTemplate(template=combine_prompt_template, input_variables=["text"])

    map_reduce_chain = load_summarize_chain(
        model,
        chain_type="map_reduce",
        map_prompt=map_prompt,
        combine_prompt=combine_prompt,
        return_intermediate_steps=return_intermediate_steps,
    )

    return map_reduce_chain({"input_documents": input_documents})
