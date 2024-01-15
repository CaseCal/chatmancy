import pytest
from unittest.mock import Mock

from chatmancy.conversation import Conversation
from chatmancy.function.function_item import FunctionItem
from chatmancy.function.function_message import (
    _FunctionRequest,
    FunctionRequestMessage,
)
from chatmancy.function.generator import FunctionItemGenerator
from chatmancy.message.message import AgentMessage, MessageQueue, UserMessage
from chatmancy.agent import Agent


@pytest.fixture
def function_item():
    return FunctionItem(
        method=lambda: True,
        name="test_function",
        description="test_function",
        params={},
        token_count=10,
    )


def test_conversation_constructor_validation():
    args = {
        "main_agent": Mock(Agent),
        "opening_prompt": "Hello!",
        "context_managers": [],
        "function_generators": [],
        "history": MessageQueue([AgentMessage(content="Hello!")]),
        "name": "TestConversation",
    }
    # Test invalid input types in the constructor
    with pytest.raises(TypeError):
        kwargs = args.copy()
        kwargs["main_agent"] = "not_an_agent"
        Conversation(
            **kwargs,
        )

    with pytest.raises(TypeError):
        kwargs = args.copy()
        kwargs["opening_prompt"] = 42
        Conversation(
            **kwargs,
        )

    with pytest.raises(TypeError):
        kwargs = args.copy()
        kwargs["context_managers"] = "not_a_list"
        Conversation(
            **kwargs,
        )

    with pytest.raises(TypeError):
        kwargs = args.copy()
        kwargs["context_managers"] = ["list_of_non_context_managers"]
        Conversation(
            **kwargs,
        )

    with pytest.raises(TypeError):
        kwargs = args.copy()
        kwargs["history"] = "not_a_message_queue"
        Conversation(**kwargs)

    with pytest.raises(TypeError):
        kwargs = args.copy()
        kwargs["context"] = 42
        Conversation(**kwargs)


def test_conversation_send_message():
    # Create a mock main agent
    main_agent = Mock(Agent)
    conversation = Conversation(main_agent)
    response_message = AgentMessage(content="Hello, human!")
    main_agent.get_response_message.return_value = response_message

    # Send the message
    user_message = UserMessage(content="Hello, bot!")
    response = conversation.send_message(user_message)

    # Assert that the main agent's get_response_message method was called
    main_agent.get_response_message.assert_called_once()
    assert response == response_message


def test_conversation_send_str_message():
    # Create a mock main agent
    main_agent = Mock(Agent)
    conversation = Conversation(main_agent)
    response_message = AgentMessage(content="Hello, human!")
    main_agent.get_response_message.return_value = response_message

    # Send the message
    response = conversation.send_message("Hello, bot!")

    # Assert that the main agent's get_response_message method was called
    main_agent.get_response_message.assert_called_once()
    assert response == response_message


def test_conversation_update_context():
    # Create a mock main agent
    main_agent = Mock(Agent)
    conversation = Conversation(main_agent)

    # Mock a ContextManager and its get_context_updates method
    context_manager = Mock()
    context_manager.get_context_updates.return_value = {"key": "value"}

    # Set the conversation's context_managers to the mock context_manager
    conversation.context_managers = [context_manager]

    # Call the _update_context method
    conversation._update_context()

    # Assert that the context_manager's get_context_updates method was called
    context_manager.get_context_updates.assert_called_once()

    # Assert that the context was updated with the result from get_context_updates
    assert conversation._context == {"key": "value"}


def test_conversation_create_functions(function_item):
    # Create a Conversation instance with the main agent
    conversation = Conversation(Mock(Agent))

    # Mock a FunctionItemGenerator and its generate_functions method
    function_generator = Mock(FunctionItemGenerator)
    function_generator.generate_functions.return_value = [function_item]

    # Set the conversation's function_generators to the mock function_generator
    conversation.function_generators = [function_generator]

    # Mock a Message and call the _create_functions method
    message = UserMessage(content="Test message")
    functions = conversation._create_functions(
        message, conversation.user_message_history.copy(), conversation._context
    )

    # Assert that the function_generator's generate_functions method was called
    function_generator.generate_functions.assert_called_once_with(
        input_message=message,
        history=conversation.user_message_history.copy(),
        context=conversation._context,
    )

    # Assert that the returned functions list is not empty
    assert functions


@pytest.mark.parametrize("auto_call", [True, False])
def test_handle_function_request_message(auto_call):
    # Create a Conversation instance with the main agent
    conversation = Conversation(Mock(Agent))

    # Mock a  FunctionRequestMessage and item
    function_request_1 = _FunctionRequest(
        name="test_function",
        args={"x": 1},
        func_item=None,
        id="test1",
    )
    function_request_2 = _FunctionRequest(
        name="test_function",
        args={"x": 2},
        func_item=None,
        id="test2",
    )

    function_item = Mock(
        FunctionItem,
        auto_call=auto_call,
        call_method=lambda x: x,
    )
    function_item.name = "test_function"

    function_request_message = FunctionRequestMessage(
        requests=[function_request_1, function_request_2]
    )

    # Call the _handle_function_request method
    response = conversation._handle_function_request_message(
        function_request_message, [function_item]
    )

    if auto_call:
        assert len(response) == 2
        assert response[0].content == "1"
        assert response[1].content == "2"

    else:
        assert isinstance(response, FunctionRequestMessage)
        assert response == FunctionRequestMessage(
            requests=[function_request_1, function_request_2]
        )


def test_auto_call_agent_requests():
    # Mock a  FunctionRequestMessage and item
    function_request = _FunctionRequest(
        name="test_function",
        args={"x": 1},
        func_item=None,
        id="test1",
    )
    function_request_message = FunctionRequestMessage(requests=[function_request])

    function_item = Mock(
        FunctionItem,
        auto_call=True,
    )
    function_item.name = "test_function"
    function_item.call_method.return_value = "1"

    # Create a mock main agent
    main_agent = Mock(Agent)
    function_item_generator = Mock(FunctionItemGenerator)
    function_item_generator.generate_functions.return_value = [function_item]
    conversation = Conversation(
        main_agent, function_generators=[function_item_generator]
    )

    # Mock agent behavior
    def mock_respond(message, history, **kwargs):
        if message.content == "Run a function":
            return function_request_message
        else:
            return AgentMessage(content="I ran it!")

    main_agent.get_response_message = mock_respond

    # Send the message
    user_message = UserMessage(content="Run a function")
    response = conversation.send_message(user_message)

    # Assert that the main agent's get_response_message method was called
    assert response == AgentMessage(content="I ran it!")
    function_item.call_method.assert_called_once_with(x=1)
