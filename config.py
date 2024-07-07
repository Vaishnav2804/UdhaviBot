from dotenv import load_dotenv
import os

load_dotenv()

GEMINI_API_KEY = os.getenv("OPENAI_API_KEY")
CHUNK_SIZE = 2400
CHUNK_OVERLAP = 200

