# import pytest


# from chatmancy.common import ChatModel, Message, TokenHandler
# from chatmancy.function import FunctionItem


# @pytest.fixture
# def token_handler() -> TokenHandler:
#     return TokenHandler.from_model(ChatModel.GPT3)


# def test_count_tokens(token_handler: TokenHandler):
#     assert token_handler.count_tokens("Hello, world!") == 4
#     assert token_handler.count_tokens("This is a sentence.") == 5


# def test_count_function_tokens(token_handler: TokenHandler):
#     function = FunctionItem(
#         method=lambda x: x,
#         name="test_function",
#         description="This is a test function.",
#     )
#     assert token_handler.count_function_tokens(function) == 35


# def test_create_message(token_handler: TokenHandler):
#     message: Message = token_handler.create_message("test_user", "Hello, world!")
#     assert message.agent_name == "test_user"
#     assert message.content == "Hello, world!"
#     assert message.token_count == 4
