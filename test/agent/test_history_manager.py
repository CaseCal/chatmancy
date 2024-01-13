# import pytest
# from unittest.mock import Mock

# # Assuming the necessary imports from your code are already done here
# from chatmancy.agent.history import (
#     HistoryGenerator,
#     StaticHistoryGenerator,
#     HistoryManager,
# )
# from chatmancy.common import Message, MessageQueue, TokenHandler
# from chatmancy.common.models import ChatModel


# @pytest.fixture
# def token_handler():
#     return TokenHandler.from_model(ChatModel.GPT3)


# def test_initialize_with_list(token_handler):
#     hm = HistoryManager(["Hello", "World"], token_handler)
#     assert isinstance(hm.history_prefix, StaticHistoryGenerator)


# def test_initialize_with_history_generator(token_handler):
#     mock_history_generator = Mock(spec=HistoryGenerator)
#     hm = HistoryManager(mock_history_generator, token_handler)
#     assert hm.history_prefix == mock_history_generator


# def test_initialize_with_invalid_data(token_handler):
#     with pytest.raises(TypeError):
#         HistoryManager(123, token_handler)


# def test_validate_prefix_tokens(token_handler):
#     mock_history_generator = Mock(spec=StaticHistoryGenerator)
#     mock_history_generator.create_history.return_value.token_count = 200

#     hm = HistoryManager(mock_history_generator, token_handler)
#     hm._validate_prefix_tokens(1000, 750)

#     assert hm.total_prefix_tokens == 200
#     assert hm.available_history_tokens == 50


# def test_validate_prefix_tokens_error(token_handler):
#     mock_history_generator = Mock(spec=StaticHistoryGenerator)
#     mock_history_generator.create_history.return_value.token_count = 200

#     hm = HistoryManager(mock_history_generator, token_handler)

#     with pytest.raises(ValueError):
#         hm._validate_prefix_tokens(900, 750)


# def test_create_history(token_handler):
#     input_message = Message("user", "Hello", 50)
#     history = MessageQueue([Message("user", "Past message", 50)])

#     hm = HistoryManager(["Prefix Message"], token_handler)
#     result = hm.create_history(
#         input_message, history, context={"key": "value"}, max_history_tokens=1000
#     )

#     assert len(result) == 4  # Prefix, past message, context message, input message
#     assert "The current context is" in result[2].content
