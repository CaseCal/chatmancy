import pytest
from unittest.mock import Mock
from chatmancy.function.function_item import FunctionItem
from chatmancy.function.function_message import (
    _FunctionRequest,
    FunctionRequestMessage,
    FunctionResponseMessage,
)

from chatmancy.message import Message
from chatmancy.agent.gpt import GPTAgent
from chatmancy.agent.gpt.history import GPTHistoryManager

from openai.types.chat import ChatCompletion

from chatmancy.message.message import AgentMessage, MessageQueue, UserMessage


@pytest.fixture(autouse=True)
def patch_openai_client(monkeypatch):
    monkeypatch.setattr(
        "chatmancy.agent.gpt.model.OpenAI",
        Mock(),
    )


def test_init():
    agent = GPTAgent(
        name="test_agent",
        desc="This is a test agent.",
        model="gpt-3.5-turbo",
        system_prompt="You are a helpful chat agent.",
        token_settings={"max_prefix_tokens": 100},
    )
    assert agent.name == "test_agent"
    assert agent.desc == "This is a test agent."
    assert agent.token_settings.max_prefix_tokens == 100


def test_model_handler_max_token_override():
    agent = GPTAgent(
        name="test_agent",
        desc="This is a test agent.",
        model="gpt-3.5-turbo",
        system_prompt="You are a helpful chat agent.",
        token_settings={"max_prefix_tokens": 100},
        model_max_tokens=100,
    )
    assert agent.model_handler.max_tokens == 100


def test_raises_missing_model():
    with pytest.raises(ValueError):
        GPTAgent(
            name="test_agent",
            desc="This is a test agent.",
            model="Uunknown model",
            system_prompt="You are a helpful chat agent.",
            token_settings={"max_prefix_tokens": 100},
        )


@pytest.fixture
def mock_openai_client():
    mock_client = Mock()

    yield mock_client

    # Check correct args were passed
    call_args = mock_client.chat.completions.create.call_args[1]
    assert "model" in call_args
    assert "messages" in call_args


@pytest.fixture
def mock_openai_message_completion(mock_openai_client):
    # Mock message response
    mock_message = Mock(
        content="This is a test response.",
        finish_reason=None,
        tool_calls=None,
    )
    mock_response = Mock(
        spec=ChatCompletion,
        choices=[Mock(message=mock_message)],
        usage=Mock(completion_tokens=10),
    )

    # Update client
    mock_openai_client.chat.completions.create.return_value = mock_response

    yield mock_response


@pytest.fixture
def mock_openai_function_completion(mock_openai_client):
    # Mock message response
    mock_function = Mock(
        arguments="{}",
    )
    mock_function.name = "test_function"
    mock_message = Mock(
        content=None,
        finish_reason=None,
        tool_calls=[
            Mock(
                id="test_function",
                type="function",
                function=mock_function,
            )
        ],
    )
    mock_response = Mock(
        spec=ChatCompletion,
        choices=[Mock(message=mock_message)],
        usage=Mock(completion_tokens=10),
    )

    # Update client
    mock_openai_client.chat.completions.create.return_value = mock_response

    yield mock_response


# HISTORY MANAGER


def test_history_manager_handles_str_message():
    history_manager = GPTHistoryManager(
        system_message="This is a test history.",
        generator=["This is a test history."],
    )
    assert history_manager.system_message.sender == "system"


def test_history_manager_handles_message_message():
    history_manager = GPTHistoryManager(
        system_message=Message(
            sender="random", content="This is a test history.", token_count=99
        ),
        generator=["This is a test history."],
    )
    assert history_manager.system_message.sender == "system"
    assert history_manager.system_message.token_count == 99


def test_history_manager_raises_too_large_system_message():
    with pytest.raises(ValueError):
        GPTHistoryManager(
            system_message=Message(
                sender="random", content="This is a test history.", token_count=100
            ),
            generator=["This is a test history."],
            max_prefix_tokens=99,
        )


def test_history_create_prefix():
    history_manager = GPTHistoryManager(
        system_message="This is a test system message.",
        generator=["This is a test history."],
    )
    prefix = history_manager._create_prefix(
        input_message=Message(sender="user", content="This is a test input."),
        context={"test": "context"},
    )
    assert len(prefix) == 2
    assert prefix[0].sender == "system"
    assert prefix[0].content == "This is a test system message."
    assert prefix[1].sender == "user"
    assert prefix[1].content == "This is a test history."
    assert prefix.token_count == 13


# INTEGRATION


@pytest.mark.usefixtures("mock_openai_message_completion")
def test_agent_get_response_message(mock_openai_client):
    agent = GPTAgent(
        name="test_agent",
        desc="This is a test agent.",
        model="gpt-3.5-turbo",
        system_prompt="You are a helpful chat agent.",
        token_settings={"max_prefix_tokens": 100},
    )
    agent.model_handler._openai_client = mock_openai_client
    response = agent.get_response_message(
        input_message=Message(sender="user", content="This is a test input."),
        history=MessageQueue([UserMessage("This is a test history.")]),
        context={"test": "context"},
        functions=[
            FunctionItem(
                method=lambda: "This is a test response.",
                name="test_function",
                description="This is a test function.",
                params={},
                token_count=10,
            ),
        ],
    )
    assert response == AgentMessage(
        "This is a test response.", token_count=10, agent_name="test_agent"
    )

    assert mock_openai_client.chat.completions.create.call_args[1]


@pytest.mark.usefixtures("mock_openai_message_completion")
def test_agent_response_with_history(mock_openai_client):
    # Set agent
    agent = GPTAgent(
        name="test_agent",
        desc="This is a test agent.",
        model="gpt-3.5-turbo",
        system_prompt="You are a helpful chat agent.",
        token_settings={"max_prefix_tokens": 100},
    )
    agent.model_handler._openai_client = mock_openai_client

    # Create history
    history = MessageQueue(
        [
            UserMessage("Call a function please", token_count=10),
            FunctionRequestMessage(
                requests=[
                    _FunctionRequest(
                        name="test_function",
                        args={},
                        func_item=None,
                        id="test_function",
                    )
                ]
            ),
            FunctionResponseMessage(
                func_name="test_function",
                content="Function ran",
                func_id="test_function",
                token_count=10,
            ),
            AgentMessage("I called the function", token_count=10),
        ]
    )

    response = agent.get_response_message(
        input_message=Message(sender="user", content="Thank you"),
        history=history,
        context={"test": "context"},
    )
    assert response == AgentMessage(
        "This is a test response.", token_count=10, agent_name="test_agent"
    )

    assert mock_openai_client.chat.completions.create.call_args[1]


@pytest.mark.usefixtures("mock_openai_message_completion")
def test_trims_history(mock_openai_client):
    agent = GPTAgent(
        name="test_agent",
        desc="This is a test agent.",
        model="gpt-3.5-turbo",
        system_prompt="You are a mock chat agent.",
        token_settings={"max_prefix_tokens": 100},
    )
    agent.model_handler._openai_client = mock_openai_client
    history = MessageQueue(
        [
            UserMessage("This is really long message.", token_count=5000),
        ]
    )

    response = agent.get_response_message(
        input_message=Message(sender="user", content="This is a test input."),
        history=history,
        context={},
    )
    assert response == AgentMessage(
        "This is a test response.", token_count=10, agent_name="test_agent"
    )
    call_args = mock_openai_client.chat.completions.create.call_args[1]
    assert len(call_args["messages"]) == 2
    assert call_args["messages"][0] == {
        "role": "system",
        "content": "You are a mock chat agent.",
    }
    assert call_args["messages"][1] == {
        "role": "user",
        "content": "This is a test input.",
    }


@pytest.mark.usefixtures("mock_openai_function_completion")
def test_function_call(mock_openai_client):
    agent = GPTAgent(
        name="test_agent",
        desc="This is a test agent.",
        model="gpt-3.5-turbo",
        system_prompt="You are a mock chat agent.",
        token_settings={"max_prefix_tokens": 100},
    )
    agent.model_handler._openai_client = mock_openai_client
    history = MessageQueue(
        [
            UserMessage("This is really long message.", token_count=5000),
        ]
    )

    response = agent.call_function(
        input_message=UserMessage(content="This is a test input."),
        history=history,
        context={},
        function_item=FunctionItem(
            method=lambda: "This is a test response.",
            name="test_function",
            description="This is a test function.",
            params={},
            token_count=10,
        ),
    )
    assert isinstance(response, FunctionRequestMessage)

    call_args = mock_openai_client.chat.completions.create.call_args[1]
    assert len(call_args["messages"]) == 2
    assert call_args["messages"][0] == {
        "role": "system",
        "content": "You are a mock chat agent.",
    }
    assert call_args["tools"] == [
        {
            "type": "function",
            "function": {
                "name": "test_function",
                "description": "This is a test function.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                },
            },
        }
    ]
    assert call_args["tool_choice"] == {
        "type": "function",
        "function": {"name": "test_function"},
    }
