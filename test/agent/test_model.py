import pytest

from chatmancy.agent.model import ModelHandler
from chatmancy.message import (
    MessageQueue,
    AgentMessage,
)
from chatmancy.function import FunctionItem, FunctionRequestMessage


class MockModelHandler(ModelHandler):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_completion(self, history, functions):
        return AgentMessage(content="test")

    def call_function(self, history, function_item):
        return FunctionRequestMessage(
            requests=[],
        )


@pytest.fixture
def model_handler():
    return MockModelHandler(max_tokens=100)


def test_get_completion(model_handler):
    history = MessageQueue()
    functions = [
        FunctionItem(
            method=lambda: True,
            name="test_function",
            description="This is a test function.",
            params={},
        )
    ]
    completion = model_handler.get_completion(history, functions)
    assert isinstance(completion, AgentMessage)


def test_call_function(model_handler):
    history = MessageQueue()
    function_item = FunctionItem(
        method=lambda: True,
        name="test_function",
        description="This is a test function.",
        params={},
    )
    response = model_handler.call_function(history, function_item)
    assert isinstance(response, FunctionRequestMessage)
