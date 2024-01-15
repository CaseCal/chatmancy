from abc import ABC, abstractmethod
import logging
from typing import List, Dict, Optional

from pydantic import BaseModel

from ..agent import GPTAgent
from ..message import UserMessage, MessageQueue
from ..function import FunctionItem, FunctionRequestMessage
from ..logging import trace


class ContextManager(ABC):
    """
    A class that manages the context of a conversation.

    Attributes:
        name (str): The name of the context manager.
    """

    def __init__(self, name: str, keys: Optional[List[str]] = None) -> None:
        self.name: str = name
        self._static_keys = keys

        self.logger = logging.getLogger(f"chatmancy.ContextManager.{name}")

    @abstractmethod
    def _get_context_updates(
        self, history: MessageQueue, current_context: Dict
    ) -> Dict:
        """
        Analyzes the message history and updates the current context.

        Args:
            history (MessageQueue): The list of past messages.
            current_context (Dict): The current context.

        Returns:
            Dict: Updated context.
        """
        pass  # pragma: no cover

    def get_context_updates(self, history: MessageQueue, current_context: Dict) -> Dict:
        """
        Analyzes the message history and updates the current context.

        Args:
            history (MessageQueue): The list of past messages.
            current_context (Dict): The current context.

        Returns:
            Dict: Updated context.
        """
        updates = self._get_context_updates(history, current_context)
        if not updates:
            return {}

        # Warn if invalid
        invalid_keys = [k for k in updates.keys() if k not in self.registered_keys]
        if invalid_keys:
            self.logger.warning(
                f"Unregistered keys {invalid_keys} returned from {self.name}"
            )
        return {k: v for k, v in updates.items() if k in self.registered_keys}

    @property
    def registered_keys(self) -> List[str]:
        """
        Returns:
            List[str]: The keys that this context manager is responsible for.
        """
        if self._static_keys is not None:
            return self._static_keys
        else:
            return []


class ContextItem(BaseModel):
    name: str
    description: str
    type: str = "string"
    valid_values: Optional[List[str]] = None

    def to_function_item(self) -> FunctionItem:
        """
        Converts the ContextItem to a dictionary fitting JSON schema object specs.

        Returns:
            Dict: A dictionary representing the JSON schema object.
        """
        param = {
            "type": self.type,
            "description": self.description,
        }
        if self.valid_values is not None:
            param["enum"] = self.valid_values

        def noop(x):
            return x  # pragma: no cover

        return FunctionItem(
            method=noop,
            name=f"update_{self.name}_context",
            description=f"Update the current context for {self.name}",
            params={self.name: param},
            required=[],
            auto_call=False,
        )


class AgentContextManager(ContextManager):
    """
    A context manager that determines context using an LLM agent

    Attributes:
        name (str): The name of the context.
        context_items (List[ContextItem]): A list of context items.
        model_handler (ModelHandler): A model handler for the context.

    Methods:
        get_context_updates(history: MessageQueue) -> Dict:
            Analyzes the message history and updates the current context.
    """

    def __init__(
        self, name: str, context_item: (ContextItem | Dict), model: str = "gpt-4"
    ) -> None:
        # Validate context items and create function items
        self.context_item = ContextItem.model_validate(context_item)
        self.function_item = self.context_item.to_function_item()

        # Agent
        self._agent = GPTAgent(
            name=f"{name}_context_manager",
            desc="A context manager",
            model=model,
            system_prompt=(
                "You are a context manager. "
                "You will analyze conversations to determine the current context."
            ),
        )

        # Super
        super().__init__(name, keys=[self.context_item.name])

    @trace(name="AgentContextManager.get_context_updates")
    def _get_context_updates(
        self, history: MessageQueue, current_context: Dict
    ) -> Dict:
        """
        Analyzes the message history and updates the current context.

        * history: The list of past messages.
        """
        input_message = UserMessage(
            content="At the current point, which things are we talking about? Use "
            "the update_context functions to tell me.",
        )
        response = self._agent.call_function(
            history=history,
            function_item=self.function_item,
            input_message=input_message,
            context={},
        )
        self.logger.debug(f"Response from agent: {response}")

        if not isinstance(response, FunctionRequestMessage):
            return {}
        elif not response.requests:
            return {}
        args = response.requests[0].args
        if not args:
            return {}

        return {
            self.context_item.name: args[self.context_item.name],
        }
