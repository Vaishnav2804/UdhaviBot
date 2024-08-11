from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from pydantic import BaseModel, Field
import logging
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from langchain_google_genai import GoogleGenerativeAIEmbeddings
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


# Initialize the LLMService
llm_svc = LLMService(logger, "", retriever)
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

            audio_data = await file.read()
            file_location = "output.wav"
            with open(file_location, "wb") as f:
                f.write(audio_data)

            gemini_resp = gemini.speech_to_text()
            response_dict = json_chain.invoke({"query": gemini_resp})

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
        print(user_language_code, user_input, user_language)

        docs = chroma.similarity_search(user_input)
        context = ""
        i=0
        for doc in docs:
            if i>3:
                break
            context += doc.page_content
            i+=1

        if context == "":
            return "I don't have an answer to this question."

        print(f"Context is: {context}")

        prompt = f"""You are a highly knowledgeable assistant specializing in Indian government schemes. Your task is to provide clear, accurate, 
        and actionable information to users about various government programs related to areas like education, healthcare, agriculture, and insurance. 
        Your responses should be grounded in the provided context and include details about the scheme name, specific benefits, and eligibility criteria. 
        The response should be tailored to the user's needs and presented in three distinct sections: Scheme Name, Benefits, and Eligibility. 
        Ensure the information is delivered in a straightforward, conversational manner without using markdown formatting. 
        Do not include any * or # in the output and use numbers for bullet points if needed.
        Give output within 3000 bytes.

        Example Query: {user_input}

        Context to use in the response: {context}"""
        
        prompt += f'Strictly give me the answer in {user_language}. Language code: {user_language_code}'

        # response = llm_svc.conversational_rag_chain().invoke(user_input)

        response = llm.invoke(prompt)

        gemini.tts(response.content, user_language_code)

        return response.content

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
