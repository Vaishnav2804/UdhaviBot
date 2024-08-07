from typing import Optional
from langchain_google_vertexai import ChatVertexAI

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import (
    ChatPromptTemplate,
    PromptTemplate,
    HumanMessagePromptTemplate
)
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from processing.documents import format_documents
from langchain_core.vectorstores import VectorStoreRetriever


def _initialize_llm(model: str) -> tuple[Optional[ChatGoogleGenerativeAI], Optional[str]]:
    """
    Initializes the LLM instance.

    Returns:
        A tuple containing:
        - The initialized ChatGoogleGenerativeAI instance if successful, otherwise None.
        - An error message as a string if initialization fails, otherwise None.
    """
    try:
        llm = ChatGoogleGenerativeAI(model=model)
        return llm, None
    except Exception as e:
        return None, str(e)


def _initialize_vertex_ai(model: str) -> ChatVertexAI:
    llm = ChatVertexAI(
        model="gemini-1.5-flash",
        temperature=0,
        max_tokens=None,
        max_retries=5,
        stop=None)
    return llm


class LLMService:
    """
    Service for managing LLM interactions and conversational RAG chain.

    Args:
        logger: Logger instance for logging.
        qa_system_prompt: The prompt for the QA system.
        web_retriever: A VectorStoreRetriever instance for retrieving web documents.
    """

    def __init__(self, logger, qa_system_prompt: str, web_retriever: VectorStoreRetriever):
        self._conversational_rag_chain = None
        self.error = None
        self._logger = logger
        self.qa_system_prompt = qa_system_prompt
        self._web_retriever = web_retriever

        self.llm, error = _initialize_llm("gemini-pro")
        self.multi_model_llm = _initialize_vertex_ai("gemini-1.5-flash")
        if error:
            self.error = error
            return

        error = self._initialize_conversational_rag_chain()
        if error:
            self.error = error
            return

    def _initialize_conversational_rag_chain(self) -> str | None:
        """
        Initializes the conversational RAG chain.

        Returns:
            An error message as a string if initialization fails, otherwise None.
        """
        try:
            # Initialize RAG (Retrieval-Augmented Generation) chain
            prompt = ChatPromptTemplate(input_variables=['context', 'question'], messages=[HumanMessagePromptTemplate(
                prompt=PromptTemplate(input_variables=['context', 'question'], template=self.qa_system_prompt))])

            # Initialize conversational RAG chain
            self._conversational_rag_chain = (
                    {"context": self._web_retriever | format_documents, "question": RunnablePassthrough()}
                    | prompt
                    | self.llm
                    | StrOutputParser()
            )

            return None
        except Exception as e:
            return str(e)

    def conversational_rag_chain(self):
        """
        Returns the initialized conversational RAG chain.

        Returns:
            The conversational RAG chain instance.
        """
        return self._conversational_rag_chain

    def get_llm(self) -> ChatGoogleGenerativeAI:
        return self.llm

    def get_multi_model_llm(self) -> ChatVertexAI:
        return self.multi_model_llm
