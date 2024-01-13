import pytest
from chatmancy.message import Message, UserMessage, MessageQueue
from chatmancy.function.generator import (
    FunctionItemGenerator,
    KeywordSortedMixin,
    StaticFunctionItemGenerator,
)
from chatmancy.function.function_item import FunctionItem
from typing import Dict, List, Set


def create_function_item(name: str, tags=Set[str]):
    return FunctionItem(
        method=lambda: True,
        name=name,
        description="Test function",
        params={},
        tags=tags,
    )


def test_abc_error():
    with pytest.raises(NotImplementedError):
        g = FunctionItemGenerator()
        g.generate_functions(None, None, None)


def test_count_keyword_hits():
    mixin = KeywordSortedMixin()
    message_content = "hello, world!"
    function_tags = {"hello", "world"}

    score = mixin._count_keyword_hits(message_content, function_tags)

    assert score == 2


def test_count_keyword_hits_relative_weighting():
    mixin = KeywordSortedMixin(relative_keyword_weighting=True)
    message_content = "hello, world!"
    function_tags = {"hello", "world"}

    score = mixin._count_keyword_hits(message_content, function_tags)

    assert score == 1


def test_count_keyword_hits_no_tags():
    mixin = KeywordSortedMixin()
    message_content = "hello, world!"
    function_tags = set()

    score = mixin._count_keyword_hits(message_content, function_tags)

    assert score == 0


def test_sort_functions():
    mixin = KeywordSortedMixin()
    functions = [
        create_function_item("func_a", tags={"apple"}),
        create_function_item("func_b", tags={"banana"}),
        create_function_item("func_ab", tags={"apple", "banana"}),
    ]
    input_message = UserMessage(content="I like apples and bananas!")
    history = MessageQueue(
        [
            UserMessage(content="Do you like apples?"),
            UserMessage(content="I like apples"),
            UserMessage(content="How about you?"),
        ]
    )
    context = {}

    sorted_functions = mixin._sort_functions(functions, input_message, history, context)

    assert len(sorted_functions) == 3
    assert sorted_functions[0].name == "func_ab"
    assert sorted_functions[1].name == "func_a"
    assert sorted_functions[2].name == "func_b"


def test_sort_functions_relative():
    mixin = KeywordSortedMixin(relative_keyword_weighting=True)
    functions = [
        create_function_item("func_a", tags={"apple"}),
        create_function_item("func_b", tags={"banana"}),
        create_function_item("func_ab", tags={"apple", "banana"}),
    ]
    input_message = UserMessage(content="I like apples")
    history = MessageQueue(
        [
            UserMessage(content="Do you like apples or bananas?"),
            UserMessage(content="I like apples"),
            UserMessage(content="How about you?"),
        ]
    )
    context = {}

    sorted_functions = mixin._sort_functions(functions, input_message, history, context)

    assert len(sorted_functions) == 3
    assert sorted_functions[0].name == "func_a"
    assert sorted_functions[1].name == "func_ab"
    assert sorted_functions[2].name == "func_b"


def test_generate_sorted_functions():
    functions = [
        create_function_item("func_a", tags={"apple"}),
        create_function_item("func_b", tags={"banana"}),
        create_function_item("func_ab", tags={"apple", "banana"}),
    ]

    class TestGenerator(KeywordSortedMixin, StaticFunctionItemGenerator):
        def __init__(self, functions: List[FunctionItem], **kwargs) -> None:
            super().__init__(functions=functions, **kwargs)

    generator = TestGenerator(functions)
    input_message = UserMessage(content="I like apples and bananas!")
    history = MessageQueue(
        [
            UserMessage(content="Do you like apples?"),
            UserMessage(content="I like apples"),
            UserMessage(content="How about you?"),
        ]
    )
    context = {}

    sorted_functions = generator.generate_functions(input_message, history, context)

    assert len(sorted_functions) == 3
    assert sorted_functions[0].name == "func_ab"
    assert sorted_functions[1].name == "func_a"
    assert sorted_functions[2].name == "func_b"


def test_static_generator():
    functions = [
        create_function_item("func_a", tags={"apple"}),
        create_function_item("func_b", tags={"banana"}),
        create_function_item("func_ab", tags={"apple", "banana"}),
    ]

    generator = StaticFunctionItemGenerator(functions)

    input_message = UserMessage(content="I like apples and bananas!")
    history = MessageQueue(
        [
            UserMessage(content="Do you like apples?"),
            UserMessage(content="I like apples"),
            UserMessage(content="How about you?"),
        ]
    )
    context = {}

    generated_functions = generator.generate_functions(input_message, history, context)

    assert len(generated_functions) == 3
    assert generated_functions[0].name == "func_a"
    assert generated_functions[1].name == "func_b"
    assert generated_functions[2].name == "func_ab"


def test_subclassing():
    class TestGenerator(FunctionItemGenerator):
        def _generate_functions(
            self, input_message: Message, history: MessageQueue, context: Dict[str, str]
        ) -> List[FunctionItem]:
            return []

    generator = TestGenerator()
    generator.generate_functions(None, None, None)
