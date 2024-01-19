from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional
import logging


from ..message import Message, MessageQueue
from ..function import (
    FunctionItem,
    FunctionRequestMessage,
)
from ..logging import trace

from .history import HistoryGenerator, HistoryManager
from .model import ModelHandler
from .functions import FunctionHandler


@dataclass
class TokenSettings:
    max_prefix_tokens: Optional[int] = None
    max_function_tokens: Optional[int] = None
    min_response_tokens: int = 750


class Agent(ABC):
    """Agent base class for generating chat responses."""

    def __init__(
        self,
        name: str,
        desc: str,
        history: (List[str] | HistoryGenerator) = None,
        token_settings: (TokenSettings | dict) = None,
        **kwargs,
    ) -> None:
        self.name = name
        self.desc = desc

        self.logger = self._initialize_logger(name, **kwargs)
        self.token_settings = self._initialize_token_settings(token_settings, **kwargs)
        self.model_handler = self._initialize_model_handler(**kwargs)
        self.history_manager = self._initialize_history_manager(history, **kwargs)
        self.function_handler = self._initialize_function_handler(**kwargs)

    def _initialize_logger(self, name: str, **_) -> logging.Logger:
        logger = logging.getLogger(f"chatmancy.Agent.{name}")
        logger.setLevel("DEBUG")
        return logger

    def _initialize_token_settings(self, token_settings, **_) -> TokenSettings:
        if isinstance(token_settings, dict):
            return TokenSettings(**token_settings)
        elif token_settings is None:
            return TokenSettings()
        return token_settings

    @abstractmethod
    def _initialize_model_handler(self, **kwargs) -> ModelHandler:
        pass  # pragma: no cover

    def _initialize_history_manager(
        self, history: (List[str] | HistoryGenerator), **kwargs
    ) -> HistoryManager:
        return HistoryManager(
            generator=history,
            max_prefix_tokens=self.token_settings.max_prefix_tokens,
        )

    def _initialize_function_handler(self, **_) -> FunctionHandler:
        return FunctionHandler(max_tokens=self.token_settings.max_function_tokens)

    @trace(name="Agent.get_response_message")
    def get_response_message(
        self,
        input_message: Message,
        history: MessageQueue,
        context: Optional[Dict] = None,
        functions: List[FunctionItem] = None,
    ) -> Message:
        """Get a response message and log the conversation.

        Args:
            input_message: The input message to respond to.
            history: The history of the conversation.
            context: Any additional context for the conversation.

        Returns:
            A Message object representing the agent's response.
        """
        self.logger.debug(f"Getting response to message: {input_message}")
        self.logger.debug(f"Context = {context}")

        # Validate input
        if not isinstance(input_message, Message):
            raise TypeError(
                (
                    f"input_message must be an instance of Message,"
                    f" not {type(input_message)}"
                )
            )

        # Get functions
        functions = self.function_handler.select_functions(
            functions, input_message, history, context
        )
        if functions is not None:
            self.logger.debug(f"Functions = {[f.name for f in functions]}")
            function_token_count = sum(f.token_count for f in functions)
        else:
            self.logger.debug("No functions selected")
            function_token_count = 0

        # Prepare history
        self.logger.debug(f"Max tokens = {self.model_handler.max_tokens}")
        self.logger.debug(f"Function token count = {function_token_count}")
        self.logger.debug(
            f"Min response tokens = {self.token_settings.min_response_tokens}"
        )
        available_tokens = (
            self.model_handler.max_tokens
            - function_token_count
            - self.token_settings.min_response_tokens
        )
        self.logger.debug(f"Available tokens = {available_tokens}")
        full_history = self.history_manager.create_history(
            input_message, history, context, max_tokens=available_tokens
        )

        # Get response from model
        response = self.model_handler.get_completion(
            history=full_history, functions=functions
        )
        response.agent_name = self.name

        return response

    def call_function(
        self,
        input_message: Message,
        history: MessageQueue,
        context: Dict,
        function_item: FunctionItem,
    ) -> FunctionRequestMessage:
        """Force the agent to call a given funuction

        Args:
            input_message: The input message to respond to.
            history: The history of the conversation.
            function_item: The function to call.

        Returns:
            The parsed response from the OpenAI API.
        """

        function_token_count = function_item.token_count

        # Prepare history
        available_tokens = (
            self.model_handler.max_tokens
            - function_token_count
            - self.token_settings.min_response_tokens
        )
        full_history = self.history_manager.create_history(
            input_message, history, context, max_tokens=available_tokens
        )

        # Get response from model
        response = self.model_handler.call_function(
            history=full_history, function_item=function_item
        )

        return response

    def give_function_response(
        self,
        history: MessageQueue,
    ) -> Message:
        """ """

        # Prepare history
        available_tokens = (
            self.model_handler.max_tokens - self.token_settings.min_response_tokens
        )
        full_history = self.history_manager.create_history(
            None, history, None, max_tokens=available_tokens
        )

        # Get response from model
        self.logger.debug("Getting response to function request with history:")
        for message in full_history:
            self.logger.debug(f"  {message}")
        response = self.model_handler.get_completion(
            history=full_history, functions=None
        )

        return response
