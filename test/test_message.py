import pytest

from collections import deque

from chatmancy.message.message import Message, UserMessage, AgentMessage, MessageQueue


# MESSAGE
def test_message_token_count():
    message = Message(sender="user", content="Hello, world!")
    assert message.token_count == 4


def test_message_token_count_override():
    message = Message(sender="user", content="Hello, world!", token_count=10)
    assert message.token_count == 10


def test_user_message():
    message = UserMessage(content="Hello, world!")
    assert message.sender == "user"
    assert message.content == "Hello, world!"
    assert message.token_count == 4


def test_agent_message():
    message = AgentMessage(content="Hello, world!")
    assert message.sender == "assistant"
    assert message.content == "Hello, world!"
    assert message.token_count == 4
    assert message.agent_name == "assistant"


# MESSAGE QUEUE


@pytest.fixture
def message():
    return Message(sender="user", content="Hello, world!")


@pytest.fixture
def messages():
    return [
        AgentMessage(content="Hi, how can I help?"),
        UserMessage(content="What's the weather like?"),
        AgentMessage(content="It's sunny today!"),
        UserMessage(content="Great!"),
    ]


def test_message_queue_init():
    queue = MessageQueue()
    assert isinstance(queue, deque)
    assert len(queue) == 0


def test_message_queue_init_with_iterable(messages):
    queue = MessageQueue(messages)
    assert isinstance(queue, deque)
    assert len(queue) == 4
    assert queue[0] == messages[0]
    assert queue[1] == messages[1]
    assert queue[2] == messages[2]
    assert queue[3] == messages[3]


def test_message_queue_validate():
    queue = MessageQueue()
    message_dict = {"sender": "user", "content": "Hello, world!"}
    assert isinstance(queue._validate(message_dict), Message)

    with pytest.raises(TypeError):
        queue._validate(None)


def test_message_queue_append(message):
    queue = MessageQueue()
    queue.append(message)
    assert len(queue) == 1
    assert queue[0] == message


def test_message_queue_appendleft(message):
    queue = MessageQueue()
    queue.appendleft(message)
    assert len(queue) == 1
    assert queue[0] == message


def test_message_queue_extend(messages):
    queue = MessageQueue()
    queue.extend(messages)
    assert len(queue) == 4
    assert queue[0] == messages[0]
    assert queue[1] == messages[1]
    assert queue[2] == messages[2]
    assert queue[3] == messages[3]


def test_message_queue_add():
    queue1 = MessageQueue([Message(sender="user", content="Hello")])
    queue2 = MessageQueue([Message(sender="agent", content="Hi")])
    new_queue = queue1 + queue2
    assert len(new_queue) == 2
    assert new_queue[0] == queue1[0]
    assert new_queue[1] == queue2[0]


def test_message_queue_copy(messages):
    queue = MessageQueue(messages)
    copy_queue = queue.copy()
    assert len(copy_queue) == 4
    assert copy_queue[0] == queue[0]
    assert copy_queue is not queue


def test_message_queue_get_last_n_tokens():
    queue = MessageQueue(
        [
            Message(sender="user", content="Hello", token_count=2),
            Message(sender="agent", content="Hi", token_count=1),
            Message(sender="user", content="How are you?", token_count=5),
            Message(sender="agent", content="I'm good", token_count=3),
        ]
    )

    messages = queue.get_last_n_tokens(8)
    assert len(messages) == 2
    assert messages[0] == queue[2]
    assert messages[1] == queue[3]

    messages = queue.get_last_n_tokens(7)
    assert len(messages) == 1

    messages = queue.get_last_n_tokens(9)
    assert len(messages) == 3


def test_message_queue_get_last_n_tokens_exclude(messages):
    queue = MessageQueue(
        [
            Message(sender="user", content="Hello", token_count=2),
            Message(sender="agent", content="Hi", token_count=1),
            Message(sender="user", content="How are you?", token_count=5),
            Message(sender="agent", content="I'm good", token_count=3),
        ]
    )
    messages = queue.get_last_n_tokens(8, exclude_types=(UserMessage,))
    assert len(messages) == 2
    for m in messages:
        assert not isinstance(m, UserMessage)


def test_message_queue_get_last_n_messages(messages):
    queue = MessageQueue(messages)
    messages = queue.get_last_n_messages(2)
    assert len(messages) == 2
    assert messages[0] == queue[2]
    assert messages[1] == queue[3]


def test_message_queue_get_last_n_messages_exclude(messages):
    queue = MessageQueue(messages)
    messages = queue.get_last_n_messages(2, exclude_types=(UserMessage,))
    assert len(messages) == 2
    for m in messages:
        assert not isinstance(m, UserMessage)


def test_message_queue_token_count():
    queue = MessageQueue(
        [
            Message(sender="user", content="Hello", token_count=2),
            Message(sender="agent", content="Hi", token_count=1),
            Message(sender="user", content="How are you?", token_count=5),
            Message(sender="agent", content="I'm good", token_count=3),
        ]
    )
    assert queue.token_count == 11


def test_message_queue_repr(messages):
    queue = MessageQueue(messages)
    assert repr(queue) == "MessageQueue(4 items)"
