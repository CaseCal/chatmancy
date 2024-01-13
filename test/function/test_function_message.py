import pytest

from chatmancy.function import (
    FunctionRequestMessage,
    FunctionResponseMessage,
    FunctionItem,
)
from chatmancy.function.function_message import _FunctionRequest


@pytest.fixture
def function_item_add():
    return FunctionItem(
        name="add",
        description="Adds two numbers",
        params={
            "a": {"type": "number", "description": "First number"},
            "b": {"type": "number", "description": "Second number"},
        },
        method=lambda a, b: a + b,
        auto_call=True,
    )


def test_response_message_init():
    message = FunctionResponseMessage(
        func_name="get_weather", content="The weather is sunny", func_id="1"
    )
    assert message.sender == "function"
    assert message.content == "The weather is sunny"
    assert message.token_count == 4


def test_request_message_init():
    req1 = _FunctionRequest(name="add", args={"a": 1, "b": 2}, func_item=None, id="1")
    message = FunctionRequestMessage(requests=[req1])
    assert message.sender == "assistant"
    assert message.content == "Request to run functions ['add']"


def test_request_message_init_from_dict():
    req1_dict = {
        "name": "add",
        "args": {"a": 1, "b": 2},
        "func_item": None,
        "id": "1",
    }
    message = FunctionRequestMessage(requests=[req1_dict])
    assert message.sender == "assistant"
    assert message.content == "Request to run functions ['add']"


def test_request_message_with_approvals():
    fi = FunctionItem(
        name="send_email",
        description="Send an email",
        params={},
        method=lambda: "Email sent!",
        auto_call=False,
    )
    req1 = {
        "name": "send_email",
        "args": {},
        "func_item": fi,
        "id": "1",
    }
    message = FunctionRequestMessage(requests=[req1])
    approvals = message.approvals_required
    assert len(approvals) == 1
    assert approvals[0].name == "send_email"


def test_function_to_response(function_item_add):
    req = _FunctionRequest(
        name="add", args={"a": 1, "b": 2}, func_item=function_item_add, id="1"
    )

    response = FunctionRequestMessage._function_to_response(req)
    assert isinstance(response, FunctionResponseMessage)
    assert response.func_name == "add"
    assert response.content == "3"


def test_function_to_response_with_error(function_item_add):
    req = _FunctionRequest(
        name="add",
        args={"a": "Bad input", "b": "2"},
        func_item=function_item_add,
        id="1",
    )

    response = FunctionRequestMessage._function_to_response(req)
    assert isinstance(response, FunctionResponseMessage)
    assert response.func_name == "add"
    assert "Error running function add" in response.content


def test_function_to_denial(function_item_add):
    fi = FunctionItem(
        name="send_email",
        description="Send an email",
        params={},
        method=lambda: "Email sent!",
        auto_call=False,
    )
    req = _FunctionRequest(name="send_email", args={}, func_item=fi, id="1")
    response = FunctionRequestMessage._function_to_denial(req)
    assert isinstance(response, FunctionResponseMessage)
    assert response.func_name == "send_email"
    assert response.content == "Function send_email denied."


def test_create_response(function_item_add):
    message = FunctionRequestMessage(
        requests=[
            _FunctionRequest(
                name="add", args={"a": 1, "b": 2}, func_item=function_item_add, id="1"
            )
        ]
    )

    responses = message.create_responses()
    assert len(responses) == 1
    assert responses[0].func_name == "add"
    assert responses[0].content == "3"


def test_create_response_mixed_approval(function_item_add):
    email_fi = FunctionItem(
        name="send_email",
        description="Send an email",
        params={},
        method=lambda: "Email sent!",
        auto_call=False,
    )
    req1 = _FunctionRequest(name="send_email", args={}, func_item=email_fi, id="1")
    req2 = _FunctionRequest(
        name="add", args={"a": 1, "b": 2}, func_item=function_item_add, id="2"
    )
    req3 = _FunctionRequest(name="send_email", args={}, func_item=email_fi, id="3")

    message = FunctionRequestMessage(requests=[req1, req2, req3])

    responses = message.create_responses(approved_ids=["1"])
    assert len(responses) == 3
    for response in responses:
        if response.func_id == "1":
            assert response.content == "Email sent!"
        elif response.func_id == "2":
            assert response.content == "3"
        elif response.func_id == "3":
            assert response.content == "Function send_email denied."


def test_create_response_empty():
    message = FunctionRequestMessage(requests=[])
    responses = message.create_responses()
    assert len(responses) == 0
