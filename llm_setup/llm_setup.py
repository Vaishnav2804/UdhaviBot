from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    PromptTemplate,
)
from langchain_core.runnables.history import (
    RunnableWithMessageHistory,
    RunnablePassthrough,
)
from langchain_openai import ChatOpenAI

import prompts as prompts
import services.documents_processing as documents_processing
# Local imports
from config import OPENAI_API_KEY, OPENAI_MODEL
from models.project_details import ProjectDetails


class LLMService:
    def __init__(self, web_retriever, logger):
        """
        Initializes the LLMService with the given web retriever and logger.

        Args:
            web_retriever: An instance for retrieving web documents.
            logger: An instance for logging errors and information.
        """
        self.logger = logger
        self.web_retriever = web_retriever
        self.history_aware_retriever = None
        self.rag_chain = None
        self.conversational_rag_chain = None
        self.questions_suggestion_rag_chain = None
        self.json_parser = None
        self.store = {}
        self.error = None

        try:
            self.llm = ChatOpenAI(openai_api_key=OPENAI_API_KEY, model=OPENAI_MODEL)
            self._initialize_history_aware_retriever()
            self._initialize_rag_chain()
            self._initialize_conversational_rag_chain()
            self._initialize_json_parser()
            self._initialize_questions_suggestion()

        except Exception as e:
            self.error = e
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
            if session_id not in self.store:
                self.store[session_id] = ChatMessageHistory()
            return self.store[session_id]
        except Exception as e:
            self.logger.error(f"Exception in _get_session_history: {e}")
            raise

    def _initialize_history_aware_retriever(self):
        """
        Initializes the history-aware retriever.
        """
        try:
            contextualize_q_prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", prompts.contextualize_q_system_prompt),
                    MessagesPlaceholder("chat_history"),
                    ("human", "{input}"),
                ]
            )

            self.history_aware_retriever = create_history_aware_retriever(
                self.llm, self.web_retriever, contextualize_q_prompt
            )
        except Exception as e:
            self.logger.error(f"Exception in initialize_history_aware_retriever: {e}")
            raise

    def _initialize_rag_chain(self):
        """
        Initializes the RAG (Retrieval-Augmented Generation) chain.
        """
        try:
            qa_system_prompt = prompts.Prompt_Message_To_RAG
            qa_prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", qa_system_prompt),
                    MessagesPlaceholder("chat_history"),
                    ("human", "{input}"),
                ]
            )
            question_answer_chain = create_stuff_documents_chain(self.llm, qa_prompt)

            self.rag_chain = create_retrieval_chain(
                self.history_aware_retriever, question_answer_chain
            )
        except Exception as e:
            self.logger.error(f"Exception in initialize_rag_chain: {e}")
            raise

    def _initialize_conversational_rag_chain(self):
        """
        Initializes the conversational RAG chain.
        """
        try:
            self.conversational_rag_chain = RunnableWithMessageHistory(
                self.rag_chain,
                self._get_session_history,
                input_messages_key="input",
                history_messages_key="chat_history",
                output_messages_key="answer",
            )
        except Exception as e:
            self.logger.error(f"Exception in initialize_conversational_rag_chain: {e}")
            raise

    def _initialize_json_parser(self):
        """
        Initializes the JSON parser for project details.
        """
        try:
            parser = JsonOutputParser(pydantic_object=ProjectDetails)
            json_prompt = PromptTemplate(
                template=prompts.Json_Prompt,
                input_variables=["query"],
                partial_variables={"format_instructions": parser.get_format_instructions()},
            )

            self.json_parser = json_prompt | self.llm | parser
        except Exception as e:
            self.logger.error(f"Exception in initialize_json_parser: {e}")
            raise

    def _initialize_questions_suggestion(self):
        """
        Initializes the questions suggestion RAG chain.
        """
        try:
            questions_suggestion = PromptTemplate(
                template=prompts.question_suggestion_prompt,
                input_variables=["context", "question"]
            )

            questions_suggestion_rag_web = (
                    {"context": self.web_retriever | documents_processing.format_documents,
                     "question": RunnablePassthrough()}
                    | questions_suggestion
                    | self.llm
                    | StrOutputParser()
            )

            self.questions_suggestion_rag_chain = questions_suggestion_rag_web
        except Exception as e:
            self.logger.error(f"Exception in initialize_questions_suggestion: {e}")
            raise

    # Getters
    def get_web_retriever(self):
        """
        Returns the web retriever.

        Returns:
            The web retriever instance.
        """
        try:
            return self.web_retriever
        except Exception as e:
            self.logger.error(f"Exception in get_web_retriever: {e}")
            raise

    def get_llm(self):
        """
        Returns the LLM instance.

        Returns:
            The LLM instance.
        """
        try:
            return self.llm
        except Exception as e:
            self.logger.error(f"Exception in get_llm: {e}")
            raise

    def get_conversational_rag_chain(self):
        """
        Returns the conversational RAG chain.

        Returns:
            The conversational RAG chain instance.
        """
        try:
            return self.conversational_rag_chain
        except Exception as e:
            self.logger.error(f"Exception in get_conversational_rag_chain: {e}")
            raise

    def get_questions_suggestion_rag_chain(self):
        """
        Returns the questions suggestion RAG chain.

        Returns:
            The questions suggestion RAG chain instance.
        """
        try:
            return self.questions_suggestion_rag_chain
        except Exception as e:
            self.logger.error(f"Exception in get_questions_suggestion_rag_chain: {e}")
            raise

    def get_json_parser(self):
        """
        Returns the JSON parser.

        Returns:
            The JSON parser instance.
        """
        try:
            return self.json_parser
        except Exception as e:
            self.logger.error(f"Exception in get_json_parser: {e}")
            raise
