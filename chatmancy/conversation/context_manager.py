import copy
from dataclasses import dataclass
from typing import List, Dict, Optional

from chatmancy.message.message import UserMessage

from ..agent import Agent
from ..message import (
    MessageQueue,
)
from ..function import FunctionItem, FunctionRequestMessage
from ..logging import trace


class ContextManager:
    """
    A class that manages the context of a conversation.

    Attributes:
        name (str): The name of the context manager
        .
    Methods:
        get_context_updates(history: MessageQueue, current_context: Dict) -> Dict:
            Analyzes the message history and updates the current context.
    """

    def __init__(
        self,
        name: str,
    ) -> None:
        self.name: str = name

    def get_context_updates(self, history: MessageQueue, current_context: Dict) -> Dict:
        """
        Analyzes the message history and updates the current context.

        * history: The list of past messages.
        """
        return {}


@dataclass
class ContextItem:
    name: str
    description: str
    type: str = "string"
    valid_values: Optional[List[str]] = None

    def to_dict(self) -> Dict:
        """
        Converts the ContextItem to a dict fitting JSON schema object specs.

        :return: A dictionary representing the JSON schema object.
        """
        json_obj = {
            "type": self.type,
            "description": self.description,
        }
        if self.valid_values is not None:
            json_obj["enum"] = self.valid_values
        return json_obj

    @staticmethod
    def to_function_item(items: List["ContextItem"]) -> FunctionItem:
        def noop(x):
            return x

        params = {ci.name: ci.to_dict() for ci in items}
        return FunctionItem(
            method=noop,
            name="update_context",
            description="Update the current context",
            params=params,
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
        self, name: str, context_items: List[(ContextItem | Dict)], model: str = "gpt-4"
    ) -> None:
        self.name: str = name

        # Check if context_items is a list of dictionaries
        if context_items and isinstance(context_items[0], dict):
            # Convert each dictionary to a ContextItem object
            self.context_items = [
                ContextItem(**item_dict) for item_dict in context_items
            ]
        else:
            self.context_items = context_items
        self.function_item = ContextItem.to_function_item(self.context_items)

        # Store Context item important values
        self.context_item_map = {ci.name: ci for ci in self.context_items}

        # Agent
        self._agent = Agent(
            name=f"{name}_context_manager",
            desc="A context manager",
            model=model,
            system_message=(
                "You are a context manager. "
                "You will analyze conversations to determine the current context."
            ),
            functions=[self.function_item],
        )

    @trace(name="AgentContextManager.get_context_updates")
    def get_context_updates(self, history: MessageQueue, current_context: Dict) -> Dict:
        """
        Analyzes the message history and updates the current context.

        * history: The list of past messages.
        """
        input_message = UserMessage(
            content="At the current point, which things are we talking about? Use "
            "the update_context function to tell me.",
        )

        response = self._agent.call_function(
            history=history,
            function_item=self.function_item,
            input_message=input_message,
            context={},
        )
        if not isinstance(response, FunctionRequestMessage):
            return {}
        elif not response.requests:
            return {}

        return self._validate_arguments(response.requests[0].args)

    def _validate_arguments(self, arguments: Dict) -> Dict:
        # Names
        arguments = {
            k: v
            for k, v in arguments.items()
            if k in [ci.name for ci in self.context_items]
        }

        # Valid values
        for arg_name, arg_value in copy.copy(arguments).items():
            ci = self.context_item_map[arg_name]

            if (ci.valid_values is not None) and (arg_value not in ci.valid_values):
                arguments.pop(arg_name)

        return arguments
