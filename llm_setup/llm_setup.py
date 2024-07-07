from typing import Tuple, Optional, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    PromptTemplate,
)
from langchain_core.runnables.history import (
    RunnableWithMessageHistory,
    RunnablePassthrough,
)


def _initialize_llm() -> Tuple[Optional[ChatGoogleGenerativeAI], Optional[str]]:
    """
    Initializes the LLM instance.

    Returns:
        A tuple containing the LLM instance and an error message (if any).
    """
    try:
        llm = ChatGoogleGenerativeAI(model="gemini-pro")
        return llm, None
    except Exception as e:
        return None, str(e)


class LLMService:
    def __init__(self, logger):
        self._conversational_rag_chain = None
        self.error = None
        self._store = {}
        self._logger = logger

        self.llm, error = _initialize_llm()
        if error:
            self.error = error
            return

        error = self._initialize_conversational_rag_chain()
        if error:
            self.error = error
            return

    def _get_session_history(self, session_id: str) -> BaseChatMessageHistory:
        """
        Retrieves the session history for a given session ID.

        Args:
            session_id (str): The session ID.

        Returns:
            BaseChatMessageHistory: The session history.
        """
        try:
            if session_id not in self._store:
                self._store[session_id] = ChatMessageHistory()
            return self._store[session_id]
        except Exception as e:
            self._logger.error(f"Exception in _get_session_history: {e}")
            raise

    def _initialize_conversational_rag_chain(self) -> Optional[str]:
        """
        Initializes the conversational RAG chain.

        Returns:
            An error message (if any).
        """
        try:
            # Initialize history-aware retriever
            contextualize_q_prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", """Given a chat history and the latest user question \
        which might reference context in the chat history, formulate a standalone question \
        which can be understood without the chat history. Do NOT answer the question, \
        just reformulate it if needed and otherwise return it as is."""),
                    MessagesPlaceholder("chat_history"),
                    ("human", "{input}"),
                ]
            )

            web_retriever = None  # Assuming this needs to be defined or passed somehow
            history_aware_retriever = create_history_aware_retriever(
                self.llm, web_retriever, contextualize_q_prompt
            )

            # Initialize RAG (Retrieval-Augmented Generation) chain
            qa_system_prompt = ("""
            Context: {context}.
            Input:{input}.
            
            You are a chatbot to assist and empower you by providing valuable information on 
            various government policies related to education, healthcare (with a focus on maternal and children), 
            agriculture, and insurance. Use context and answer within the 
            context only. If any questions are asked beyond the context, say "I don't know."
            """)

            qa_prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", qa_system_prompt),
                    MessagesPlaceholder("chat_history"),
                    ("human", "{input}"),
                ]
            )
            question_answer_chain = create_stuff_documents_chain(self.llm, qa_prompt)

            rag_chain = create_retrieval_chain(
                history_aware_retriever, question_answer_chain
            )

            # Initialize conversational RAG chain
            self._conversational_rag_chain = RunnableWithMessageHistory(
                rag_chain,
                self._get_session_history,
                input_messages_key="input",
                history_messages_key="chat_history",
                output_messages_key="answer",
            )

            return None
        except Exception as e:
            return str(e)

    def conversational_rag_chain(self):
        return self._conversational_rag_chain

    def get_llm(self) -> Tuple[Optional[ChatGoogleGenerativeAI], Optional[str]]:
        """
        Returns the LLM instance.

        Returns:
            A tuple containing the LLM instance and an error message (if any).
        """
        if self.llm is None:
            return None, "LLM not initialized"

        return self.llm, None
