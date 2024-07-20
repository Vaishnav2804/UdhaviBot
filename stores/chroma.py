from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.vectorstores import VectorStoreRetriever
from typing import Optional
from langchain.schema import Document


def store_embeddings(documents: list[Document], embeddings: HuggingFaceEmbeddings) -> (
        tuple)[Optional[VectorStoreRetriever], Optional[str]]:
    """
    Store embeddings for the documents using HuggingFace embeddings and Chroma vectorstore.
    Returns a tuple containing the retriever object and an error message if any.
    """
    try:
        vectorstore_web = Chroma.from_documents(documents=documents, embedding=embeddings)
        return vectorstore_web.as_retriever(), None
    except Exception as e:
        return None, {
            'error': 'error creating VectorStoreRetriever from chroma DB',
            'exception': str(e)
        }.__str__()
