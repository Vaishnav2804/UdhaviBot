from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from pydantic import BaseModel
import logging
from fastapi.middleware.cors import CORSMiddleware

# Import your existing modules
from llm_setup.llm_setup import LLMService
import configs.config as config
import scraper
import processing.documents as document_processing
from stores.chroma import store_embeddings
import speech_to_text.gemini as gemini

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"],
                   allow_headers=["*"])

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
{context} and answer for this query in a simple manner: {question}."""

# Initialize the LLMService
llm_svc = LLMService(logger, prompt, retriever)
if llm_svc.error is not None:
    logger.error(f"Error initializing LLM service: {llm_svc.error}")

llm = llm_svc.get_llm()


@app.post("/chat")
async def chat(
        text: str = Form(None),
        file: UploadFile = File(None)
):
    try:
        user_input = ""
        user_language_code = ""
        user_language = ""
        if file:
            # Handle audio input
            audio_data = await file.read()
            file_location = "output.wav"
            with open(file_location, "wb") as f:
                f.write(audio_data)

            response_dict = gemini.speech_to_text()

        elif text:
            # Handle text input
            user_input = text
            llm_response = llm.invoke(f"""{user_input} for this question
                                        Give the output in a json format:
                                        language:"Original audio language", text :"Proper english translation of the 
                                        question such that an englishman can understand, language_code: Google Text to Speech language code of the original 
                                        language that the question was asked in" : """)
            llm_response = response.text
            llm_response_list = response.splitlines()
            llm_response_list.pop(0)
            llm_response_list.pop(-1)
            llm_response = "\n".join(response_list)
            try:
                response_dict = json.loads(response)
            except Exception as e:
                print("Error while converting to dictionary"+e.__str__())
                raise e
        else:
            raise HTTPException(status_code=400, detail="Either text or audio file is required")

        user_language = response_dict['language']
        user_input = response_dict['text']
        user_language_code  = response_dict["language_code"]

        user_input += f'Strictly give me the answer in {user_language}'
        # Invoke the conversational RAG chain with the user's input
        response = llm_svc.conversational_rag_chain().invoke(user_input)

        

        return response

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="An internal error occurred")

    gemini.tts(response.text,user_language_code)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
