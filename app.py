import logging

from llm_setup.llm_setup import LLMService
import configs.config as config
from services.scraper import scrape_and_get_store_vector_retriever

if __name__ == '__main__':
    # logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # set environment variables
    config.set_envs()

    store_vector_retriever, error = scrape_and_get_store_vector_retriever()
    if error:
        print(f"Error in embedding contents: {error}")
        exit(0)

    prompt = """
    You are a chatbot to assist under-deserved people with governments schemes. 
    Use this Context: {context} and answer for this query in an simple manner: {question}
    """

    # get llm service
    llm_svc = LLMService(logger,prompt,store_vector_retriever)
    if llm_svc.error is not None:
        print(f"Error in initializing llm service: {llm_svc.error}")
        exit(0)

    # get llm instance to make llm calls
    try:
        response = llm_svc.conversational_rag_chain().invoke("Tell me what you know")

        print(str(response))

    except Exception as e:
        print(str(e))
