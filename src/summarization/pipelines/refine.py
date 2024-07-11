from langchain_core.prompts import PromptTemplate
from langchain.chains.summarize import load_summarize_chain


# Refine prompts
question_prompt_template = """
                  Please provide a summary of the following text.
                  TEXT: {text}
                  SUMMARY:
                  """

refine_prompt_template = """
              Write a concise summary of the following text delimited by triple backquotes.
              Return your response in bullet points which covers the key points of the text.
              ```{text}```
              BULLET POINT SUMMARY:
              """


def refine(model, input_documents: list, return_intermediate_steps: bool = False):
    """
    The function executes the langchain refine pipeline for summarising

    :arg model: the langauge model on which summarization would be done on
    :arg input_documents: list of the pages on which summarization would work on
    :arg return_intermediate_steps: if True, the intermediate steps will be included in the response

    :return: summarised output for the documents
    """
    question_prompt = PromptTemplate(template=question_prompt_template, input_variables=["text"])
    refine_prompt = PromptTemplate(template=refine_prompt_template, input_variables=["text"])

    refine_chain = load_summarize_chain(
        model,
        chain_type="refine",
        question_prompt=question_prompt,
        refine_prompt=refine_prompt,
        return_intermediate_steps=return_intermediate_steps,
    )

    return refine_chain.invoke({"input_documents": input_documents})