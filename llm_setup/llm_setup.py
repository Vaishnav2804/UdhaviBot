from typing import Tuple, Optional, Any
from langchain_google_genai import ChatGoogleGenerativeAI


class LLMService:
    def __init__(self):
        self.llm = None
        self.error = None
        try:
            self.llm = ChatGoogleGenerativeAI(model="gemini-pro")
        except Exception as e:
            self.error = e
            return

    def get_llm(self) -> Tuple[Optional[ChatGoogleGenerativeAI], Optional[Any]]:
        """
        Returns the LLM instance.

        Returns:
            The LLM instance.
        """
        if self.llm is None:
            return None, f"LLM not initialized"

        return self.llm, None
