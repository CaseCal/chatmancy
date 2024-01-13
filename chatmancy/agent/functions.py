from typing import Dict, List

from ..message import Message, MessageQueue
from ..function import (
    FunctionItem,
)


class FunctionHandler:
    def __init__(
        self,
        max_tokens: int = None,
        **kwargs,
    ) -> None:
        # Tokens
        if not isinstance(max_tokens, (int, type(None))):
            raise TypeError(
                f"Invalid max_tokens. Expected an int or None, got {type(max_tokens)}."
            )
        self._max_tokens = max_tokens

    def select_functions(
        self,
        functions: List[FunctionItem],
        input_message: Message,
        history: MessageQueue = None,
        context: Dict[str, str] = None,
    ):
        """
        Returns a list of functions that are applicable to the given
        input message, history, and context.

        Args:
            functions (List[FunctionItem]): A list of FunctionItem objects representing
                the available functions.
            input_message (Message): The input message to be processed.
            history (MessageQueue): A lMessageQueue representing the
                conversation history.
            context (Dict[str, Any]): A dictionary containing contextual
                information about the conversation.

        Returns:
            List[FunctionItem]: A list of FunctionItem objects representing the
              applicable functions.
        """
        functions = self._sort_functions(
            functions, input_message=input_message, history=history, context=context
        )

        # Trim
        functions = self._trim_functions(functions)

        return functions

    def _sort_functions(self, functions: List[FunctionItem], **kwargs):
        """
        Sorts the given list of functions by their relevance to the input message.
        Override for more advanced handling

        Args:
            functions (List[FunctionItem]): A list of FunctionItem objects representing
                the available functions.
            input_message (Message): The input message to be processed.

        Returns:
            List[FunctionItem]: A list of FunctionItem objects representing the
              applicable functions.
        """
        return functions

    def _trim_functions(self, functions: List[FunctionItem]):
        # Add functions until max token count is hit
        if self._max_tokens is None:
            return functions
        else:
            token_count = 0
            funcs = []
            for func in functions:
                if func.token_count is None:
                    func.token_count = self._token_handler.count_function_tokens(func)
                token_count += func.token_count
                if token_count > self._max_tokens:
                    break
                funcs.append(func)
            return funcs
