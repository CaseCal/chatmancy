import pytest
from unittest.mock import Mock
from chatmancy.agent.functions import FunctionHandler
from chatmancy.function.function_item import FunctionItem
from chatmancy.message.message import Message, MessageQueue


def test_init_max_tokens_error():
    with pytest.raises(TypeError):
        FunctionHandler(max_tokens="bad value")


def test_select_functions():
    handler = FunctionHandler(max_tokens=100)
    functions = [
        Mock(FunctionItem, token_count=10),
        Mock(FunctionItem, token_count=20),
        Mock(FunctionItem, token_count=30),
    ]
    input_message = Mock(Message)
    history = Mock(MessageQueue)
    context = {"key": "value"}

    selected_functions = handler.select_functions(
        functions, input_message, history=history, context=context
    )

    assert len(selected_functions) == 3
    assert selected_functions[0].token_count == 10
    assert selected_functions[1].token_count == 20
    assert selected_functions[2].token_count == 30


def test_select_functions_no_max_tokens():
    handler = FunctionHandler()
    functions = [
        Mock(FunctionItem, token_count=10),
        Mock(FunctionItem, token_count=20),
        Mock(FunctionItem, token_count=30),
    ]
    input_message = Mock(Message)
    history = Mock(MessageQueue)
    context = {"key": "value"}

    selected_functions = handler.select_functions(
        functions, input_message, history=history, context=context
    )

    assert len(selected_functions) == 3
    assert selected_functions[0].token_count == 10
    assert selected_functions[1].token_count == 20
    assert selected_functions[2].token_count == 30


def test_trim_functions():
    handler = FunctionHandler(max_tokens=50)
    functions = [
        Mock(FunctionItem, token_count=10),
        Mock(FunctionItem, token_count=20),
        Mock(FunctionItem, token_count=30),
    ]

    trimmed_functions = handler._trim_functions(functions)

    assert len(trimmed_functions) == 2
    assert trimmed_functions[0].token_count == 10
    assert trimmed_functions[1].token_count == 20


def test_trim_functions_no_max_tokens():
    handler = FunctionHandler()
    functions = [
        Mock(FunctionItem, token_count=10),
        Mock(FunctionItem, token_count=20),
        Mock(FunctionItem, token_count=30),
    ]

    trimmed_functions = handler._trim_functions(functions)

    assert len(trimmed_functions) == 3
    assert trimmed_functions[0].token_count == 10
    assert trimmed_functions[1].token_count == 20
    assert trimmed_functions[2].token_count == 30


def test_trim_functions_with_missing_tokens():
    handler = FunctionHandler(max_tokens=100)
    functions = [
        Mock(FunctionItem, token_count=None),
        Mock(FunctionItem, token_count=20),
        Mock(FunctionItem, token_count=30),
    ]

    with pytest.raises(ValueError):
        handler._trim_functions(functions)
