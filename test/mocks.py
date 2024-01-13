from typing import List
from unittest.mock import Mock

from chatmancy.agent.base import ModelHandler
from chatmancy.message import Message, MessageQueue
from chatmancy.function import FunctionItem


class MockModelHandler(ModelHandler):
    def __init__(self):
        mock_model = Mock()
        mock_model.max_tokens = 1000
        mock_model.model = "mock"
        mock_model.cost_per_token = 0.001

        self.model = mock_model
        self.logger = Mock()

    def submit_request(
        self,
        input_message: Message,
        history: MessageQueue,
        functions: List[FunctionItem] | None = None,
        **kwargs
    ) -> Message:
        return Message("Mock", "Hello, I'm a mock model handler!", 6)

    def call_function(
        self,
        input_message: Message,
        history: MessageQueue,
        function_item: FunctionItem,
        **kwargs
    ) -> Message:
        return Message("Mock", "Hello, I'm a mock model handler!", 6)
