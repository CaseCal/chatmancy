from dataclasses import dataclass
from typing import Dict, List, Optional
import logging


from ..message import Message, MessageQueue
from ..function import (
    FunctionItem,
    FunctionItemGenerator,
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


class Agent:
    """Agent base class for generating chat responses."""

    def __init__(
        self,
        name: str,
        desc: str,
        history: (List[str] | HistoryGenerator) = None,
        functions: (List[FunctionItem] | FunctionItemGenerator) = None,
        token_settings: (TokenSettings | dict) = None,
        **kwargs,
    ) -> None:
        self.name = name
        self.desc = desc

        self.logger = self.initialize_logger(name, **kwargs)
        self.token_settings = self.initialize_token_settings(token_settings, **kwargs)
        self.model_handler = self.initialize_model_handler(**kwargs)
        self.history_manager = self.initialize_history_manager(history, **kwargs)
        self.function_handler = self.initialize_function_handler(functions, **kwargs)

    def initialize_logger(self, name: str, **kwargs):
        logger = logging.getLogger(f"Agent.{name}")
        logger.setLevel("DEBUG")
        return logger

    def initialize_token_settings(self, token_settings, **kwargs):
        if isinstance(token_settings, dict):
            return TokenSettings(**token_settings)
        elif token_settings is None:
            return TokenSettings()
        return token_settings

    def initialize_model_handler(self, **kwargs):
        return ModelHandler()

    def initialize_history_manager(
        self, history: (List[str] | HistoryGenerator), **kwargs
    ):
        return HistoryManager(
            generator=history,
            max_prefix_tokens=self.token_settings.max_prefix_tokens,
        )

    def initialize_function_handler(self, functions, **kwargs):
        return FunctionHandler(
            generator=functions, max_tokens=self.token_settings.max_function_tokens
        )

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

        # Get functions
        functions = self.function_handler.select_functions(
            functions, input_message, history, context
        )
        self.logger.debug(f"Functions = {[f.name for f in functions]}")
        function_token_count = sum(f.token_count for f in functions)

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
        response = self.model_handler.get_completion(
            history=full_history, functions=functions
        )

        # Log and return
        self.logger.info(response.content)
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

        # Log and return
        self.logger.info(response.content)
        return response


class GPTAgent(Agent):
    """Agent class for generating chat responses using GPT-3."""

    def __init__(
        self,
        name: str,
        desc: str,
        model: str,
        system_prompt: str = "You are a helpful chat agent.",
        history: (List[str] | HistoryGenerator) = None,
        functions: (List[FunctionItem] | FunctionItemGenerator) = None,
        token_settings: (TokenSettings | dict) = None,
    ) -> None:
        """Create a new Agent instance.

        Args:
            name: The name of the agent.
            desc: A description of the agent.
        """
        super().__init__(
            name=name,
            desc=desc,
            model=model,
            system_prompt=system_prompt,
            history=history,
            functions=functions,
            token_settings=token_settings,
        )

    def initialize_model_handler(self, model: str, **kwargs):
        return ModelHandler(model=model)

    def initialize_history_manager(
        self, history: (List[str] | HistoryGenerator), system_prompt: str, **kwargs
    ):
        return HistoryManager(
            system_message=system_prompt,
            generator=history,
            max_prefix_tokens=self.token_settings.max_prefix_tokens,
        )
