from abc import ABC, abstractmethod
import json
from typing import List, Dict

from openai import OpenAI
from openai.types.chat import ChatCompletion

from ..logging import trace
from ..message import Message, AgentMessage, UserMessage, MessageQueue
from ..function import FunctionItem, FunctionResponseMessage, FunctionRequestMessage


MODEL_INFO = {
    "gpt-4-1106-preview": {
        "max_tokens": 128000,
    },
    "gpt-4-vision-preview": {
        "max_tokens": 128000,
    },
    "gpt-4": {
        "max_tokens": 8192,
    },
    "gpt-4-32k": {
        "max_tokens": 32768,
    },
    "gpt-4-0613": {
        "max_tokens": 8192,
    },
    "gpt-4-32k-0613": {
        "max_tokens": 32768,
    },
    "gpt-4-0314": {
        "max_tokens": 8192,
    },
    "gpt-4-32k-0314": {
        "max_tokens": 32768,
    },
    "gpt-3.5-turbo-1106": {
        "max_tokens": 16385,
    },
    "gpt-3.5-turbo": {
        "max_tokens": 4096,
    },
    "gpt-3.5-turbo-16k": {
        "max_tokens": 16385,
    },
}


class ModelHandler(ABC):
    """
    Abstract base class for ModelHandlers.
    ModelHandlers convert Messages and Functions into the correct format
    for an LLM API or model, and convert responses from the model into Messages
    and FunctionRequestMessages.
    """

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
        pass

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
        pass


class GPTModelHandler:
    def __init__(
        self,
        model: str,
        max_tokens: int = None,
        agent_name: str = "assistant",
        **kwargs,
    ) -> None:
        """
        Initializes a new instance of the ModelHandler class.
        ModelHandlers convert Messages and Functions into the correct format
        for the OpenAI SDK, and convert responses from the OpenAI SDK into Messages
          and FunctionRequestMessages.

        Args:
            model (str): The name of the OpenAI model to use.
            max_tokens (int): The maximum number of tokens the model can use.
                Pass this is explicitly if the given model is not known.
            **kwargs: Additional keyword arguments to pass to the OpenAI client.

        """
        self._model = model
        self._openai_client = OpenAI(**kwargs)
        self._agent_name = agent_name
        if max_tokens is not None:
            self.max_tokens = max_tokens
        else:
            try:
                self.max_tokens = MODEL_INFO[model]["max_tokens"]
            except KeyError:
                raise ValueError(
                    f"Model name {model} not found. Please manally pass max_tokens"
                )

    @trace(name="Model.submit_request")
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
        args = {
            "model": self._model,
            "messages": self._convert_history(history),
        }

        # Add functions if present and enabled
        if functions:
            args["tools"] = [
                {"type": "function", "function": f.to_dict()} for f in functions
            ]

        # Call and parse
        response: ChatCompletion = self._openai_client.chat.completions.create(**args)
        return self._parse_gpt_response(response)

    def call_function(
        self,
        history: MessageQueue,
        function_item: FunctionItem,
    ):
        """
        Force the agent to call a given funuction

        Args:
            history (MessageQueue): The message history.
            function_item (FunctionItem): The function to call.

        Returns:
            The parsed response from the OpenAI API.
        """
        # Call and parse
        response = self._openai_client.chat.completions.create(
            model=self._model,
            messages=self._convert_history(history),
            tools=[{"type": "function", "function": function_item.to_dict()}],
            tool_choice={
                "type": "function",
                "function": {"name": function_item.name},
            },
        )
        return self._parse_gpt_response(response)

    def _message_to_gpt(self, message: Message) -> Dict:
        if isinstance(message, FunctionResponseMessage):
            return {
                "role": "tool",
                "name": message.func_name,
                "content": message.content,
                "tool_call_id": message.func_id,
            }
        elif isinstance(message, FunctionRequestMessage):
            return self._func_request_to_gpt(message)
        if isinstance(message, AgentMessage):
            role = "assistant"
        elif isinstance(message, UserMessage):
            role = "user"
        else:
            role = message.sender
        return {"role": role, "content": message.content}

    def _func_request_to_gpt(self, message: FunctionRequestMessage) -> Dict:
        return {
            "role": "assistant",
            "content": None,
            "tool_calls": [
                {
                    "id": f.id,
                    "type": "function",
                    "function": {
                        "name": f.name,
                        "arguments": json.dumps(f.args),
                    },
                }
                for f in message.requests
            ],
        }

    def _parse_gpt_response(self, response: ChatCompletion) -> Message:
        """
        Take the response from the GPT API and convert it into a Message object.
        If the response is a function call, return a FunctionRequestMessage instead.
        """
        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls
        if tool_calls:
            requests = [
                {
                    "func_name": tool_call.function.name,
                    "func_args": json.loads(tool_call.function.arguments),
                    "func_id": tool_call.id,
                }
                for tool_call in tool_calls
            ]
            return FunctionRequestMessage(
                sender="assistant",
                requests=requests,
                token_count=response.usage.completion_tokens,
            )
        else:
            return AgentMessage(
                content=response_message.content,
                token_count=response.usage.completion_tokens,
                agent_name=self._agent_name,
            )

    def _convert_history(self, history: MessageQueue) -> List[Dict]:
        return [self._message_to_gpt(m) for m in history]
