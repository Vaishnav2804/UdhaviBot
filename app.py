from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from pydantic import BaseModel, Field
import logging
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

# Import your existing modules
from llm_setup.llm_setup import LLMService
import configs.config as config
import scraper
import processing.documents as document_processing
from stores.chroma import store_embeddings
import speech_to_text.gemini as gemini
import json
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate

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
chroma = store_embeddings(documents, config.EMBEDDINGS)
retriever = chroma.as_retriever()


# Define your desired data structure.
class Language(BaseModel):
    text: str
    language: str
    language_code: str


# Define the prompt template for the chatbot
prompt = """You are an expert chatbot trained to provide detailed and accurate information about Indian government 
schemes. Your task is to assist users by answering questions related to various government schemes such as those for 
education, healthcare, agriculture, and insurance. When responding, ensure that your answers are clear, informative, 
and based on the most recent and relevant information. If the user asks about eligibility, application processes, 
or benefits, provide specific details and guide them through the necessary steps if applicable. Always aim to offer 
helpful and precise responses tailored to their needs. Use this Context: {context} and answer for this query in a 
simple manner: {question}. Strictly accept questions within context. Give a detailed response to the user. The output 
will be used by a conversational robot, so just give output in simple text format."""

# Initialize the LLMService
llm_svc = LLMService(logger, prompt, retriever)
if llm_svc.error is not None:
    logger.error(f"Error initializing LLM service: {llm_svc.error}")

llm = llm_svc.get_llm()

parser = JsonOutputParser(pydantic_object=Language)

prompt = PromptTemplate(
    template="Answer the user query.\n{format_instructions}\n{query}\n",
    input_variables=["query"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)

json_chain = prompt | llm | parser


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

        elif text:
            # Handle text input
            user_input = text
            llm_response = json_chain.invoke({"query": f"""
            User Input: {user_input}
            
            Provide a JSON response with the following keys:
            * language: The language of the input text.
            * text: A proper English translation understandable by a native English speaker.
            * language_code: The equivalent Google Cloud Platform language code for text-to-speech.
            """})

            try:
                response_dict = llm_response
            except Exception as e:
                print("Error while converting to dictionary" + e.__str__())
                raise e
        else:
            raise HTTPException(status_code=400, detail="Either text or audio file is required")

        user_language = response_dict['language']
        user_input = response_dict['text']
        user_language_code = response_dict["language_code"]

        docs = chroma.similarity_search("user_input")
        context = ""
        for doc in docs:
            context += doc.page_content

        user_input += (f'Strictly give me the answer in {user_language}. More Context For your reference:{context}. If '
                       f'the context is not empty, frame an answer from that.')

        # Invoke the conversational RAG chain with the user's input
        response = llm_svc.conversational_rag_chain().invoke(user_input)

        gemini.tts(response, user_language_code)

        return {"Data": response}

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="An internal error occurred")


@app.get("/download")
def download_file():
    file_path = "output.mp3"  # Replace with the actual file path
    return FileResponse(file_path, media_type="audio/mpeg", filename="output.mp3")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
