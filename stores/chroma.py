from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.vectorstores import VectorStoreRetriever
from typing import Optional
from langchain.schema import Document


def store_embeddings(documents: list[Document], embeddings: GoogleGenerativeAIEmbeddings) -> Optional[Chroma]:
    """
    Store embeddings for the documents using embeddings and Chroma vectorstore.
    Returns a tuple containing the retriever object and an error message if any.
    """
    try:
        vectorstore_web = Chroma.from_documents(documents=documents, embedding=embeddings)
        return vectorstore_web
    except Exception as e:
        raise Exception(f"""error creating VectorStoreRetriever from chroma DB: {e}""")
