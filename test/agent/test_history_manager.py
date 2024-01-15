import pytest
from chatmancy.agent.history import (
    HistoryManager,
    HistoryGenerator,
    StaticHistoryGenerator,
)
from chatmancy.message.message import MessageQueue, UserMessage


def test_history_manager_init_with_list_generator():
    generator = [
        "Statement 1",
        "Statement 2",
        "Statement 3",
    ]
    history_manager = HistoryManager(generator)
    assert isinstance(history_manager, HistoryManager)
    assert isinstance(history_manager.generator, HistoryGenerator)
    assert history_manager.max_prefix_tokens is None


def test_history_manager_init_with_history_generator():
    generator = HistoryGenerator()
    history_manager = HistoryManager(generator, max_prefix_tokens=10)
    assert isinstance(history_manager, HistoryManager)
    assert history_manager.generator == generator
    assert history_manager.max_prefix_tokens == 10


def test_history_manager_init_with_invalid_generator():
    generator = "Invalid generator"
    with pytest.raises(TypeError):
        HistoryManager(generator)


def test_history_manager_create_prefix():
    generator = [
        "Statement 1",
        "Statement 2",
        "Statement 3",
    ]
    history_manager = HistoryManager(generator)
    input_message = UserMessage("Hello", 1)
    context = {"key": "value"}
    prefix = history_manager._create_prefix(input_message, context)
    assert isinstance(prefix, MessageQueue)
    assert len(prefix) == 3


def test_history_manager_create_prefix_with_max_prefix_tokens():
    generator = [
        UserMessage("Statement 1", token_count=5),
        UserMessage("Statement 2", token_count=10),
        UserMessage("Statement 3", token_count=5),
    ]
    history_manager = HistoryManager(generator, max_prefix_tokens=17)
    input_message = UserMessage("Hello", 1)
    context = {"key": "value"}
    prefix = history_manager._create_prefix(input_message, context)
    assert isinstance(prefix, MessageQueue)
    assert len(prefix) == 2


def test_static_history_generator_validates_type():
    messages = [UserMessage("Statement 1", token_count=5), "Other messages", None]
    with pytest.raises(TypeError):
        StaticHistoryGenerator(messages)


def test_history_manager_create_history():
    generator = [
        "Statement 1",
        "Statement 2",
        "Statement 3",
    ]
    history_manager = HistoryManager(generator)
    input_message = UserMessage("Hello", 1)
    history = MessageQueue()
    context = {"key": "value"}
    max_tokens = 100
    created_history = history_manager.create_history(
        input_message, history, context, max_tokens
    )
    assert isinstance(created_history, MessageQueue)
    assert len(created_history) == 4


def test_history_manager_create_raises_bad_args():
    generator = [
        "Statement 1",
        "Statement 2",
        "Statement 3",
    ]
    history_manager = HistoryManager(generator)
    input_message = UserMessage("Hello", 1)
    history = "weird history"
    context = {"key": "value"}
    max_tokens = 100
    with pytest.raises(TypeError):
        history_manager.create_history(input_message, history, context, max_tokens)


def test_history_manager_when_input_too_large():
    generator = [
        "Statement 1",
        "Statement 2",
        "Statement 3",
    ]
    history_manager = HistoryManager(generator, max_prefix_tokens=10)
    input_message = UserMessage("Hello", 11)
    history = MessageQueue()
    context = {"key": "value"}
    max_tokens = 10
    with pytest.raises(ValueError):
        history_manager.create_history(input_message, history, context, max_tokens)
