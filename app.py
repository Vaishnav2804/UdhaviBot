from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from pydantic import BaseModel
import logging

# Import your existing modules
from llm_setup.llm_setup import LLMService
import configs.config as config
import scraper
import processing.documents as document_processing
from stores.chroma import store_embeddings
import speech_to_text.gemini as gemini

app = FastAPI()

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Set environment variables
config.set_envs()

# Start web scraping if configured
if config.START_WEB_SCRAPING_MYSCHEMES:
    scraper.scrape_and_store_to_json_file()

# Convert contents from JSON file to list of Documents
documents = document_processing.load_json_to_langchain_document_schema("myschemes_scraped.json")
retriever = store_embeddings(documents, config.EMBEDDINGS)

# Define the prompt template for the chatbot
prompt = """You are an expert chatbot trained to provide detailed and accurate information about Indian 
government schemes. Your task is to assist users by answering questions related to various government schemes 
such as those for education, healthcare, agriculture, and insurance. When responding, ensure that your answers 
are clear, informative, and based on the most recent and relevant information. If the user asks about 
eligibility, application processes, or benefits, provide specific details and guide them through the necessary 
steps if applicable. Always aim to offer helpful and precise responses tailored to their needs. Use this Context: 
{context} and answer for this query in a simple manner: {question}"""

# Initialize the LLMService
llm_svc = LLMService(logger, prompt, retriever)
if llm_svc.error is not None:
    logger.error(f"Error initializing LLM service: {llm_svc.error}")

llm = llm_svc.get_llm()


class AudioResponse(BaseModel):
    response: str


@app.post("/chat")
async def chat(
        text: str = Form(None),
        file: UploadFile = File(None)
):
    try:
        if file:
            # Handle audio input
            audio_data = await file.read()
            file_location = "output.wav"
            with open(file_location, "wb") as f:
                f.write(audio_data)

            response_dict = gemini.speech_to_text()
            user_language = response_dict['language']
            user_input = response_dict['text']
        elif text:
            # Handle text input
            user_input = text
            user_language = llm.invoke(f"Just return me the language of the text: {user_input}")
        else:
            raise HTTPException(status_code=400, detail="Either text or audio file is required")

        # Invoke the conversational RAG chain with the user's input
        response = llm_svc.conversational_rag_chain().invoke(user_input)

        # Translate the response if the user's language is not English
        if user_language.lower() != "english":
            translated_response = llm.invoke(f"Translate the given text to {user_language}: {response}")
            translated_response = translated_response.content
        else:
            translated_response = response

        return AudioResponse(response=translated_response)

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="An internal error occurred")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
