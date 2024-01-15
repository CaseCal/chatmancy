from typing import Dict, List
import logging

from chatmancy.message.message import UserMessage

from ...agent.history import HistoryGenerator, HistoryManager
from ...message import Message, MessageQueue


class GPTHistoryManager(HistoryManager):
    def __init__(
        self,
        system_message: Message,
        generator: (List[str] | HistoryGenerator),
        max_prefix_tokens: int = None,
    ) -> None:
        super().__init__(generator, max_prefix_tokens)
        # System message check
        if isinstance(system_message, str):
            system_message = Message(sender="system", content=system_message)
        elif system_message.sender != "system":
            logging.getLogger("GPTAgent.HistoryManager").warning(
                (
                    "The system message should have sender 'system', "
                    "it will be replaced with a system message"
                )
            )
            system_message = Message(
                sender="system",
                content=system_message.content,
                token_count=system_message.token_count,
            )
        self.system_message = system_message

        # Token check
        if self.max_prefix_tokens is not None:
            if system_message.token_count > self.max_prefix_tokens:
                raise ValueError(
                    (
                        "The system message has more tokens than the maximum "
                        "number of prefix tokens"
                    )
                )

    def _create_prefix(
        self, input_message: Message, context: Dict[str, str]
    ) -> MessageQueue:
        prefix = super()._create_prefix(input_message, context)
        prefix.appendleft(self.system_message)
        return prefix
