from collections import deque
from copy import copy as copy_func
from typing import Any, List, Optional, Tuple, Type

from pydantic import BaseModel, Field, field_validator, ValidationInfo
import tiktoken


class Message(BaseModel):
    """
    A class that represents a message.
    """

    sender: str
    content: str
    token_count: Optional[int] = Field(validate_default=True, default=None)

    @field_validator(
        "token_count",
        mode="before",
    )
    def compute_token_count(cls, v: Any, v_info: ValidationInfo):
        if v is not None:
            return v
        enc = tiktoken.encoding_for_model("gpt-4")
        tk = len(enc.encode(v_info.data["content"]))
        return tk


class UserMessage(Message):
    def __init__(self, content: str, token_count: int = None):
        super().__init__(sender="user", content=content, token_count=token_count)


class AgentMessage(Message):
    agent_name: str = "assistant"

    def __init__(
        self,
        content: str,
        token_count: int = None,
        agent_name: str = "assistant",
        **kwargs,
    ):
        super().__init__(
            sender="assistant",
            content=content,
            token_count=token_count,
            agent_name=agent_name,
            **kwargs,
        )


class MessageQueue(deque):
    def __init__(self, iterable=None):
        super().__init__()
        if iterable is not None:
            self.extend(iterable)

    def _validate(self, message: Message):
        if isinstance(message, Message):
            return message
        else:
            try:
                return Message(**message)
            except Exception:
                raise TypeError(
                    "Only Message objects can be added to MessageQueue, "
                    f" not {type(message)}"
                )

    def append(self, message):
        validated_message = self._validate(message)
        super().append(validated_message)

    def appendleft(self, message):
        validated_message = self._validate(message)
        super().appendleft(validated_message)

    def extend(self, messages):
        for message in messages:
            self.append(message)

    def __add__(self, other):
        new_queue = MessageQueue(self)
        new_queue.extend(other)
        return new_queue

    def copy(self):
        """
        Create a shallow copy of the MessageQueue.

        # Return
        A new MessageQueue that's a copy of the original.
        """
        return copy_func(self)

    def get_last_n_tokens(self, n, exclude_types: Tuple[Type] = ()) -> List[Message]:
        """
        Return the most recent messages, up to a total token count of n.

        # Return
        List of messages whose total token count is less than n.
        """
        result = []
        current_token_sum = 0
        for message in reversed(self):
            if isinstance(message, exclude_types):
                continue

            if current_token_sum + message.token_count > n:
                break
            current_token_sum += message.token_count
            result.append(message)
        return result[::-1]  # Return messages in original order

    def get_last_n_messages(self, n, exclude_types: Tuple[Type] = ()) -> List[Message]:
        """
        Return the most recent n messages

        # Return
        List of messages
        """
        result = []
        for message in reversed(self):
            # Skip func requests by default
            if isinstance(message, exclude_types):
                continue

            if len(result) >= n:
                break
            result.append(message)
        return result[::-1]  # Return messages in original order

    @property
    def token_count(self):
        return sum(m.token_count for m in self)

    def __repr__(self):
        return f"MessageQueue({len(self)} items)"

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, MessageQueue):
            return list(self) == list(__value)
        else:
            return super().__eq__(__value)
