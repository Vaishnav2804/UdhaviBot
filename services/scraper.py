# services.py
import requests
from langchain.schema import Document
from typing import Optional, List, Tuple, Iterable
from processing.documents import load_documents, format_documents, split_documents
from processing.texts import clean_text
from stores.chroma import store_embeddings
from langchain_core.vectorstores import VectorStoreRetriever
from services import api_services
from configs.config import BASE_URL, BASE_SCHEME_URL, HEADERS, TOTAL_RESULTS, MAX_SIZE, EMBEDDINGS


def create_scheme_urls(slugs: List[str], base_scheme_url: str) -> List[str]:
    return [f"{base_scheme_url}{slug}" for slug in slugs]


def scrape_and_get_store_vector_retriever() -> Tuple[Optional[VectorStoreRetriever], Optional[str]]:
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
