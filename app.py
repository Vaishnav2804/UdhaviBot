from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from pydantic import BaseModel
import logging
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from llm_setup.llm_setup import LLMService
import configs.config as config
import scraper
import processing.documents as document_processing
from stores.chroma import store_embeddings
import speech_to_text.gemini as gemini
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate

# Initialize FastAPI app
app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Set environment variables
config.set_envs()

# Start web scraping if configured
if config.START_WEB_SCRAPING_MYSCHEMES:
    scraper.scrape_and_store_to_json_file()

# Load documents and store embeddings
documents = document_processing.load_json_to_langchain_document_schema("myschemes_scraped.json")
chroma = store_embeddings(documents, config.EMBEDDINGS)
retriever = chroma.as_retriever()


# Define the Language data model
class Language(BaseModel):
    text: str
    language: str
    language_code: str


# Initialize the LLMService
llm_svc = LLMService(logger, "", retriever)
if llm_svc.error:
    logger.error(f"Error initializing LLM service: {llm_svc.error}")

llm = llm_svc.get_llm()

# Set up the JSON output parser and prompt template
parser = JsonOutputParser(pydantic_object=Language)
prompt_template = PromptTemplate(
    template="Answer the user query.\n{format_instructions}\n{query}\n",
    input_variables=["query"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)

json_chain = prompt_template | llm | parser


@app.post("/chat")
async def chat(text: str = Form(None), file: UploadFile = File(None)):
    try:
        if file:
            audio_data = await file.read()
            file_location = "output.wav"
            with open(file_location, "wb") as f:
                f.write(audio_data)

            gemini_resp = gemini.speech_to_text(file_location)
            response_dict = json_chain.invoke({"query": gemini_resp})
        elif text:
            llm_response = json_chain.invoke({
                "query": f"""
                User Input: {text}
                Provide a JSON response with the following keys:
                * language: The language of the input text.
                * text: A proper English translation understandable by a native English speaker.
                * language_code: The equivalent Google Cloud Platform language code for text-to-speech.
                """
            })
            response_dict = llm_response
        else:
            raise HTTPException(status_code=400, detail="Either text or audio file is required")

        user_language = response_dict['language']
        user_input = response_dict['text']
        user_language_code = response_dict["language_code"]

        docs = chroma.similarity_search(user_input)
        context = " ".join(doc.page_content for doc in docs[:4])

        if not context:
            return {"message": "I don't have an answer to this question."}

        prompt = f"""
        You are a highly knowledgeable assistant specializing in Indian government schemes. 
        Your task is to provide clear, accurate, and actionable information to users about various government programs 
        related to areas like education, healthcare, agriculture, and insurance. 
        Your responses should be grounded in the provided context and include details about the scheme name, specific benefits, and eligibility criteria. 
        Ensure the information is delivered in a straightforward, conversational manner without using markdown formatting.
        Example Query: {user_input}
        Context: {context}
        Answer in {user_language}. Language code: {user_language_code}.
        """

        response = llm.invoke(prompt)
        gemini.tts(response.content, user_language_code)

        return {"response": response.content}

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="An internal error occurred")


@app.get("/download")
def download_file():
    file_path = "output.mp3"
    return FileResponse(file_path, media_type="audio/mpeg", filename="output.mp3")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
