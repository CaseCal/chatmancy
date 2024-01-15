from abc import ABC, abstractmethod
from typing import List


from ..message import AgentMessage, MessageQueue
from ..function import FunctionItem, FunctionRequestMessage


class ModelHandler(ABC):
    """
    Abstract base class for ModelHandlers.
    ModelHandlers convert Messages and Functions into the correct format
    for an LLM API or model, and convert responses from the model into Messages
    and FunctionRequestMessages.
    """

    max_tokens: int

    def __init__(self, max_tokens: int, **kwargs) -> None:
        self.max_tokens = max_tokens

    @abstractmethod
    def get_completion(
        self,
        history: MessageQueue,
        functions: List[FunctionItem] = None,
    ) -> AgentMessage:
        """
        Generates a chatbot response given a message history and optional functions.

        Args:
            history (MessageQueue): The message history to generate a response from.
            functions (List[FunctionItem], optional): A list of FunctionItem objects
                to use for generating the response. Defaults to None.

        Returns:
            ChatCompletion: The generated chatbot response.
        """
        pass  # pragma: no cover

    @abstractmethod
    def call_function(
        self,
        history: MessageQueue,
        function_item: FunctionItem,
    ) -> FunctionRequestMessage:
        """
        Force the agent to call a given funuction

        Args:
            history (MessageQueue): The message history.
            function_item (FunctionItem): The function to call.

        Returns:
            The parsed response from the OpenAI API.
        """
        pass  # pragma: no cover
