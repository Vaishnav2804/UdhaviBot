import logging
from llm_setup.llm_setup import LLMService
import configs.config as config
import scraper as scraper
import processing.documents as document_processing
from stores.chroma import store_embeddings
import tranlsation.engine as tranlsation_engine
import speech_to_text.gemini as gemini

if __name__ == '__main__':  # Entry point for the script
    logger = logging.getLogger()  # Create a logger object
    logger.setLevel(logging.INFO)  # Set the logging level to INFO

    config.set_envs()  # Set environment variables using the config module

    if config.START_WEB_SCRAPING_MYSCHEMES:
        scraper.scrape_and_store_to_json_file()

    # convert contents from json file to list of Documents of langchain schema type
    documents = document_processing.load_json_to_langchain_document_schema("myschemes_scraped.json")

    # Scrape data and get the store vector retriever
    retriever = store_embeddings(documents, config.EMBEDDINGS)

    # Define the prompt template for the chatbot
    prompt = """You are an expert chatbot trained to provide detailed and accurate information about Indian 
    government schemes. Your task is to assist users by answering questions related to various government schemes 
    such as those for education, healthcare, agriculture, and insurance. When responding, ensure that your answers 
    are clear, informative, and based on the most recent and relevant information. If the user asks about 
    eligibility, application processes, or benefits, provide specific details and guide them through the necessary 
    steps if applicable. Always aim to offer helpful and precise responses tailored to their needs. Use this Context: 
    {context} and answer for this query in a simple manner: {question}"""

    # Initialize the LLMService with logger, prompt, and store vector retriever
    llm_svc = LLMService(logger, prompt, retriever)
    if llm_svc.error is not None:  # Check if there was an error in initializing the LLMService
        print(f"Error in initializing llm service: {llm_svc.error}")
        exit(0)  # Exit the script

    llm = llm_svc.get_llm()

    try:
        tranlsation_engine.record_audio()
        response_dict = gemini.speech_to_text()
        user_language = response_dict['language']
        user_input = response_dict['text']
        # Invoke the conversational RAG chain with a sample query
        response = llm_svc.conversational_rag_chain().invoke("user_input")
        if user_language.lower() != "english":
            translated_response = llm.invoke(f"Translate the given text to {user_language}: {response}")
            translated_response = translated_response.content
        else:
            translated_response = response
        print(str(response))
        print(str(translated_response))

    except Exception as e:  # Catch any exceptions that occur
        print(str(e))  # Print the exception message
