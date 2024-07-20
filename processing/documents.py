from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from typing import Iterable


def load_documents(website: str) -> list[Document]:
    """
    Loads documents from a given website.

    Args:
        website (str): The URL of the website to load documents from.

    Returns:
        list[Document]: A list of loaded documents.
    """
    loader = WebBaseLoader(website)
    return loader.load()


def format_documents(docs: list[Document]) -> str:
    """
    Formats a list of documents into a single string.

    Args:
        docs (list[Document]): The list of documents to format.

    Returns:
        str: The formatted documents as a single string.
    """
    return "\n\n".join(doc.page_content for doc in docs)


def split_documents(documents: Iterable[Document]) -> list[Document]:
    """
    Splits documents into smaller chunks.

    Args:
        documents (Iterable[Document]): The documents to split.

    Returns:
        list[Document]: A list of split documents.
    """
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    return text_splitter.split_documents(documents)
