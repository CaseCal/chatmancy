import pytest
from chatmancy.function import FunctionItemFactory


@pytest.fixture
def custom_params():
    return {
        "a": {"type": "number", "description": "First number"},
        "b": {"type": "number", "description": "Second number"},
    }


@pytest.fixture
def factory(custom_params):
    return FunctionItemFactory(params=custom_params)


@pytest.fixture
def func_item_args():
    return {
        "method": lambda a, b: a + b,
        "name": "add",
        "description": "Add a and b",
        "params": ["a", "b"],
        "required": ["a", "b"],
        "auto_call": True,
        "tags": ["tag1", "tag2"],
    }


def test_init():
    factory = FunctionItemFactory()
    assert factory._params == {}
    assert factory._tags == []


def test_init_with_params():
    custom_params = {
        "a": {"type": "number", "description": "First number"},
        "b": {"type": "number", "description": "Second number"},
    }
    factory = FunctionItemFactory(params=custom_params)
    assert factory._params["a"].type == "number"
    assert factory._params["b"].description == "Second number"


def test_init_with_bad_params():
    # Non-string
    with pytest.raises(ValueError) as e:
        FunctionItemFactory(params={1: {"type": "number"}})
    assert "Invalid param name" in str(e.value)

    # Can't cconvert to FunctionParameter
    with pytest.raises(ValueError) as e:
        FunctionItemFactory(params={"a": {"name": "a", "type": "number"}})


def test_init_with_tags():
    tags = ["tag1", "tag2"]
    factory = FunctionItemFactory(tags=tags)
    assert factory._params == {}
    assert factory._tags == tags


def test_create_function_item(factory):
    func_item = factory.create_function_item(
        method=lambda a, b: a + b,
        name="add",
        description="Add a and b",
        params=["a", "b"],
        required=["a", "b"],
        auto_call=True,
        tags=["tag1", "tag2"],
    )

    assert func_item.name == "add"
    assert func_item.description == "Add a and b"
    assert func_item.call_method(a=1, b=2) == 3


def test_create_function_item_with_invalid_param(factory, func_item_args):
    func_item_args["params"] = ["a", "b", "c"]

    with pytest.raises(ValueError) as e:
        factory.create_function_item(**func_item_args)
    assert "Invalid param detected" in str(e.value)


def test_create_function_item_without_params(factory: FunctionItemFactory):
    func_item = factory.create_function_item(
        method=lambda: 1,
        name="no-op",
        description="Return 1",
    )

    assert func_item.name == "no-op"
    assert func_item.call_method() == 1


def test_create_function_item_with_custom_params(factory: FunctionItemFactory):
    func_item = factory.create_function_item(
        method=lambda a, b, c: a + b + c,
        name="add",
        description="Add a and b and c",
        params=["a", "b"],
        custom_params={
            "c": {"type": "number", "description": "Custom third number"},
        },
    )

    assert func_item.name == "add"
    assert func_item.description == "Add a and b and c"
    assert func_item.call_method(a=1, b=2, c=1) == 4
