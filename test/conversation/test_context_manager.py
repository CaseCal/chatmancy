from unittest.mock import Mock, patch

import pytest
from chatmancy.agent.gpt.agent import GPTAgent

from chatmancy.conversation import (
    AgentContextManager,
)
from chatmancy.conversation.context_manager import ContextItem
from chatmancy.function.function_message import (
    _FunctionRequest,
    FunctionRequestMessage,
)
from chatmancy.message.message import (
    UserMessage,
)  # Replace with the correct import path

# Define a sample history and context
sample_history = []
sample_context = {}


@pytest.fixture
def mock_agent():
    with patch("chatmancy.conversation.context_manager.GPTAgent") as mock_agent_class:
        mock_agent = Mock(spec=GPTAgent)
        mock_agent_class.return_value = mock_agent
        yield mock_agent


def test_agent_context_manager_get_context_updates(mock_agent):
    # Create an instance of AgentContextManager
    ci = ContextItem(name="item1", description="item1", valid_values=["1a", "1b"])
    context_manager = AgentContextManager(name="TestContextManager", context_item=ci)

    # Create a mock response from the GPTAgent
    mock_response = FunctionRequestMessage(
        requests=[
            _FunctionRequest(
                name=context_manager.function_item.name,
                args={context_manager.function_item.name: {"item1": "value1"}},
                id="1234",
            )
        ]
    )
    mock_agent.call_function.return_value = mock_response

    # Call the get_context_updates method
    context_updates = context_manager.get_context_updates(
        sample_history, sample_context
    )

    # Assert that the mock agent's call_function method was called
    mock_agent.call_function.assert_called_once_with(
        history=sample_history,
        function_item=context_manager.function_item,
        input_message=UserMessage(
            content=(
                "At the current point, which things are we talking about?"
                " Use the update_context functions to tell me."
            ),
            token_count=21,
        ),
        context={},
    )

    # Assert that the context_updates dictionary contains the expected values
    assert context_updates == {"item1": "value1"}
