from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from typing import Iterable


def load_documents(website: str) -> list[Document]:
    loader = WebBaseLoader(website)
    return loader.load()


def format_documents(docs: list[Document]):
    return "\n\n".join(doc.page_content for doc in docs)


def split_documents(documents: Iterable[Document]) -> list[Document]:
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    return text_splitter.split_documents(documents)
