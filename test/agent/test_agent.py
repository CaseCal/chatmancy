import pytest
from unittest.mock import Mock
from chatmancy.agent.base import (
    Agent,
    TokenSettings,
)


class MockAgent(Agent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def initialize_model_handler(self, **kwargs):
        return Mock()

    def initialize_history_manager(self, history, **kwargs):
        return Mock()

    def initialize_function_handler(self, functions, **kwargs):
        return Mock()


def test_agent_init():
    agent = MockAgent(
        name="test_agent",
        desc="test agent description",
    )
    assert isinstance(agent, Agent)
