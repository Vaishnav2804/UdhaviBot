from dotenv import load_dotenv
import os
import getpass as getpass
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()

CHUNK_SIZE = 2400
CHUNK_OVERLAP = 200

BASE_URL = "https://api.myscheme.gov.in/search/v4/schemes?lang=en&q=%5B%5D&keyword=&sort=&size="
BASE_SCHEME_URL = "https://www.myscheme.gov.in/schemes/"
HEADERS = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'en-US,en;q=0.9',
    'origin': 'https://www.myscheme.gov.in',
    'priority': 'u=1, i',
    'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
    'x-api-key': 'tYTy5eEhlu9rFjyxuCr7ra7ACp4dv1RH8gWuHTDc'
}
TOTAL_RESULTS = 2389
MAX_SIZE = 100
EMBEDDINGS = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-mpnet-base-v2",
    model_kwargs={"device": "cpu"},
)

START_WEB_SCRAPING_MYSCHEMES = False


def set_envs():
    if "GOOGLE_API_KEY" not in os.environ:
        os.environ["GOOGLE_API_KEY"] = getpass.getpass(os.getenv("GOOGLE_API_KEY"))
