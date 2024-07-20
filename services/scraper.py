# services.py
import requests
from langchain.schema import Document
from typing import Optional
from processing.documents import load_documents, format_documents, split_documents
from processing.texts import clean_text
from stores.chroma import store_embeddings
from langchain_core.vectorstores import VectorStoreRetriever
from services import api_services
from configs.config import BASE_URL, BASE_SCHEME_URL, HEADERS, TOTAL_RESULTS, MAX_SIZE, EMBEDDINGS


def create_scheme_urls(slugs: list[str], base_scheme_url: str) -> list[str]:
    """
    Creates a list of URLs for schemes based on extracted slugs and base scheme URL.

    Args:
        slugs (list[str]): A list of extracted scheme slugs.
        base_scheme_url (str): The base URL for scheme details.

    Returns:
        list[str]: A list of complete URLs for individual schemes.
    """
    return [f"{base_scheme_url}{slug}" for slug in slugs]


def scrape_and_get_store_vector_retriever() -> tuple[Optional[VectorStoreRetriever], Optional[str]]:
    """
    Scrapes website content from fetched schemes and creates a VectorStore retriever.

    This function performs the following steps:
    1. Fetches scheme slugs using the `api_services.fetch_schemes` function.
    2. Creates a list of full URLs for individual schemes.
    3. Iterates through the URLs, performing the following for each:
        - Loads documents from the website.
        - Formats and cleans the document content.
        - Creates a Document object with the cleaned content.
    4. Splits the documents into smaller chunks.
    5. Stores the document embeddings using the `store_embeddings` function.
    6. Returns a VectorStore retriever and a combined error message (if any)

    Args:

    Returns:
        tuple: A tuple containing:
            - Optional[VectorStoreRetriever]: A VectorStore retriever instance if successful, otherwise None.
            - Optional[str]: A semicolon-separated string of error messages encountered during scraping or storing embeddings, or None if no errors occurred.

    """
    slugs, errors = api_services.fetch_schemes(BASE_URL, TOTAL_RESULTS, MAX_SIZE, HEADERS)
    if errors:
        print(f"Errors occurred: {errors}")

    urls = create_scheme_urls(slugs, BASE_SCHEME_URL)

    documents = []
    error_messages = []

    for website_url in urls:
        try:
            website_documents = load_documents(website_url)
            if website_documents:
                formatted_content = format_documents(website_documents)
                cleaned_content = clean_text(formatted_content)
                documents.append(Document(page_content=cleaned_content))
            else:
                error_message = f"Failed to load document for website: {website_url}"
                error_messages.append(error_message)
        except Exception as e:
            error_message = f"Error processing {website_url}: {e}"
            error_messages.append(error_message)

    retriever, store_embeddings_error = store_embeddings(split_documents(documents), EMBEDDINGS)
    if store_embeddings_error:
        return None, f"Error storing embeddings: {store_embeddings_error}"

    return retriever, "; ".join(error_messages) if error_messages else None
