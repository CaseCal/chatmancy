import pytest
from unittest.mock import Mock
from chatmancy.agent.base import Agent, TokenSettings
from chatmancy.function.function_item import FunctionItem
from chatmancy.function.function_message import _FunctionRequest, FunctionRequestMessage
from chatmancy.message.message import AgentMessage, MessageQueue, UserMessage


@pytest.fixture
def mock_model_handler():
    return Mock()


class MockAgent(Agent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _initialize_model_handler(self, **kwargs):
        mock_handler = Mock()
        mock_handler.max_tokens = 1000
        return mock_handler


def test_agent_init():
    agent = MockAgent(
        name="test_agent",
        desc="test agent description",
    )
    assert isinstance(agent, Agent)


def test_agent_init_with_token_settings_dict():
    agent = MockAgent(
        name="test_agent",
        desc="test agent description",
        token_settings={
            "max_prefix_tokens": 100,
            "max_function_tokens": 100,
            "min_response_tokens": 100,
        },
    )
    assert isinstance(agent, Agent)
    assert agent.token_settings.max_prefix_tokens == 100
    assert agent.token_settings.max_function_tokens == 100
    assert agent.token_settings.min_response_tokens == 100


def test_agent_init_with_token_settings_object():
    agent = MockAgent(
        name="test_agent",
        desc="test agent description",
        token_settings=TokenSettings(
            max_prefix_tokens=100, max_function_tokens=100, min_response_tokens=100
        ),
    )
    assert isinstance(agent, Agent)
    assert agent.token_settings.max_prefix_tokens == 100
    assert agent.token_settings.max_function_tokens == 100
    assert agent.token_settings.min_response_tokens == 100


def test_get_response_message():
    agent = MockAgent(
        name="test_agent",
        desc="test agent description",
    )
    agent.model_handler.get_completion.return_value = AgentMessage(
        "Hello", token_count=1
    )
    history = MessageQueue()
    assert agent.get_response_message(
        UserMessage("Hello", 1), history=history
    ) == AgentMessage("Hello", token_count=1, agent_name="test_agent")


def test_get_response_message_with_str():
    agent = MockAgent(
        name="test_agent",
        desc="test agent description",
    )
    history = MessageQueue()
    with pytest.raises(TypeError):
        agent.get_response_message("Hello", history=history)


def test_get_response_message_with_functions():
    agent = MockAgent(
        name="test_agent",
        desc="test agent description",
    )

    history = MessageQueue()
    functions = [
        Mock(
            name="test_function",
            method=lambda x: x,
            token_count=10,
        )
    ]
    request = _FunctionRequest(
        name="test_function", args={}, func_item=Mock(FunctionItem), id="1"
    )
    agent.model_handler.get_completion.return_value = FunctionRequestMessage(
        requests=[request], token_count=1
    )
    assert agent.get_response_message(
        UserMessage("Hello", 1), history=history, functions=functions
    ) == FunctionRequestMessage(
        requests=[request],
        token_count=1,
        function_item=functions[0],
        agent_name="test_agent",
    )


def test_force_function_call():
    agent = MockAgent(
        name="test_agent",
        desc="test agent description",
    )

    history = MessageQueue()
    func_item = Mock(FunctionItem, token_count=1)
    mock_req_message = Mock(FunctionRequestMessage, token_count=1)
    agent.model_handler.call_function.return_value = mock_req_message
    function_request = agent.call_function(
        UserMessage("Hello", 1), history=history, context={}, function_item=func_item
    )
    assert function_request == mock_req_message
