# import pytest

# from chatmancy.function import FunctionItem, FunctionHandler, KeywordFunctionHandler
# from chatmancy.common import ChatModel, MessageQueue, TokenHandler


# @pytest.fixture
# def functions():
#     return [
#         FunctionItem(
#             method=lambda: "Hello",
#             name="greet",
#             description="Greeting function",
#             token_count=10,
#         ),
#         FunctionItem(
#             method=lambda: "Goodbye",
#             name="goodbye",
#             description="Goodbye function",
#             token_count=10,
#         ),
#         FunctionItem(
#             method=lambda: "Rainy",
#             name="weather",
#             description="Weather Function",
#             token_count=10,
#         ),
#     ]


# def test_without_max_tokens(functions: list[FunctionItem]):
#     token_handler = TokenHandler.from_model(ChatModel.GPT3)
#     function_handler = FunctionHandler(token_handler)

#     assert function_handler.get_functions(functions, "hi", [], {}) == functions


# def test_token_limits(functions: list[FunctionItem]):
#     token_handler = TokenHandler.from_model(ChatModel.GPT3)
#     function_handler = FunctionHandler(token_handler, max_tokens=10)

#     assert function_handler._max_tokens == 10
#     assert function_handler.get_functions(functions, "hi", [], {}) == [functions[0]]

#     function_handler._max_tokens = 25
#     assert function_handler.get_functions(functions, "hi", [], {}) == functions[:2]

#     function_handler._max_tokens = 50
#     assert function_handler.get_functions(functions, "hi", [], {}) == functions[:3]


# def test_keyword_function_handler():
#     # Define some functions
#     functions = [
#         FunctionItem(
#             method=lambda: "Hello",
#             name="greet",
#             description="Greeting function",
#             token_count=10,
#             tags={"greeting", "hello", "hi"},
#         ),
#         FunctionItem(
#             method=lambda: "Goodbye",
#             name="goodbye",
#             description="Goodbye function",
#             token_count=10,
#             tags={"goodbye", "bye", "see you"},
#         ),
#         FunctionItem(
#             method=lambda: "Rainy",
#             name="weather",
#             description="Weather Function",
#             token_count=10,
#             tags={"weather", "rain", "temperature"},
#         ),
#     ]

#     # Create a token handler
#     token_handler = TokenHandler.from_model(ChatModel.GPT3)

#     # Create a keyword function handler
#     keyword_handler = KeywordFunctionHandler(
#         functions=functions,
#         token_handler=token_handler,
#         max_tokens=20,
#         search_depth=5,
#         decay_rate=0.5,
#         relative_keyword_weighting=False,
#     )

#     # Test get_functions method
#     input_message = token_handler.create_message(
#         "user", "Hello, what's the temperature today?"
#     )
#     history = MessageQueue()
#     context = {}
#     result = keyword_handler.get_functions(
#         functions=functions,
#         input_message=input_message,
#         history=history,
#         context=context,
#     )
#     assert len(result) == 2
#     assert result[0].name == "greet"
#     assert result[1].name == "weather"

#     # Test _count_keyword_hits method
#     message_content = "hello, what's the temperature today?"
#     function_tags = {"greeting", "hello", "hi"}
#     result = keyword_handler._count_keyword_hits(message_content, function_tags)
#     assert result == 1
