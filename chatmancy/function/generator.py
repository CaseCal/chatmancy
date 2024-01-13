from abc import ABC
from typing import Dict, List, Set

from ..message import Message, MessageQueue
from .function_item import (
    FunctionItem,
)


class FunctionItemGenerator(ABC):
    def _generate_functions(
        self, input_message: Message, history: MessageQueue, context: Dict[str, str]
    ) -> List[FunctionItem]:
        raise NotImplementedError(
            "FunctionGenerator is an abstract class. Please use a subclass."
        )

    def generate_functions(
        self, input_message: Message, history: MessageQueue, context: Dict[str, str]
    ) -> List[FunctionItem]:
        functions = self._generate_functions(input_message, history, context)
        return functions


class KeywordSortedMixin(FunctionItemGenerator):
    def __init__(
        self,
        search_depth: int = 5,
        decay_rate: float = 0.5,
        relative_keyword_weighting: bool = False,
        **kwargs,
    ) -> None:
        """
        Mixin to return generated fuunctions in keyword-sorted order.
        This ensrues that more relevant functions are presented first, and less likely
        to be cut off by the token limit.
        """
        super().__init__(**kwargs)
        self._relative_keyword_weighting = relative_keyword_weighting
        self._search_depth = search_depth
        self._decay_rate = decay_rate

    def generate_functions(
        self, input_message: Message, history: MessageQueue, context: Dict[str, str]
    ) -> List[FunctionItem]:
        functions = super().generate_functions(input_message, history, context)
        functions = self._sort_functions(functions, input_message, history, context)
        return functions

    def _sort_functions(
        self,
        functions: List[FunctionItem],
        input_message,
        history: MessageQueue,
        context,
    ) -> List[FunctionItem]:
        targets: List[Message] = [
            input_message,
            *reversed(history.get_last_n_messages(self._search_depth)),
        ]

        # Preprocessing messages
        message_contents = [msg.content.lower() for msg in targets]

        # Initializing keyword hits
        keyword_hits = {f.name: 0 for f in functions}

        # Counting keywords, weighted by recency
        for depth, message_content in enumerate(message_contents):
            decay_factor = self._decay_rate**depth
            for f in functions:
                keyword_hits[f.name] += (
                    self._count_keyword_hits(message_content, f.tags) * decay_factor
                )

        sorted_functions = sorted(
            functions, key=lambda f: keyword_hits[f.name], reverse=True
        )
        return sorted_functions

    def _count_keyword_hits(
        self, message_content: str, function_tags: Set[str]
    ) -> float:
        if not function_tags:
            return 0

        score = sum(
            (1 if not self._relative_keyword_weighting else 1 / len(function_tags))
            for keyword in function_tags
            if keyword.lower() in message_content
        )
        return score


class StaticFunctionItemGenerator(FunctionItemGenerator):
    def __init__(self, functions: List[FunctionItem]) -> None:
        self._functions = functions

    def generate_functions(
        self, input_message: Message, history: MessageQueue, context: Dict[str, str]
    ) -> List[FunctionItem]:
        return self._functions
