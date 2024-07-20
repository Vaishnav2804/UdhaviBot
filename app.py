import logging
from llm_setup.llm_setup import LLMService
import configs.config as config
from services.scraper import scrape_and_get_store_vector_retriever

if __name__ == '__main__':  # Entry point for the script
    logger = logging.getLogger()  # Create a logger object
    logger.setLevel(logging.INFO)  # Set the logging level to INFO

    config.set_envs()  # Set environment variables using the config module

    # Scrape data and get the store vector retriever
    store_vector_retriever, error = scrape_and_get_store_vector_retriever()
    if error:  # Check if there was an error in scraping and embedding
        print(f"Error in embedding contents: {error}")  # Print the error message
        exit(0)  # Exit the script

    # Define the prompt template for the chatbot
    prompt = """
    You are a chatbot to assist under-deserved people with government schemes. 
    Use this Context: {context} and answer for this query in a simple manner: {question}
    """

    # Initialize the LLMService with logger, prompt, and store vector retriever
    llm_svc = LLMService(logger, prompt, store_vector_retriever)
    if llm_svc.error is not None:  # Check if there was an error in initializing the LLMService
        print(f"Error in initializing llm service: {llm_svc.error}")
        exit(0)  # Exit the script

    try:
        # Invoke the conversational RAG chain with a sample query
        response = llm_svc.conversational_rag_chain().invoke("Tell me what you know")
        print(str(response))

    except Exception as e:  # Catch any exceptions that occur
        print(str(e))  # Print the exception message
