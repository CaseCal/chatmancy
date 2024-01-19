import pytest
from chatmancy.function import FunctionItem, FunctionParameter


def test_init():
    func_item = FunctionItem(
        method=lambda a, b: a + b,
        name="add",
        description="Add a and b",
        params={
            "a": FunctionParameter(type="number", description="First number"),
            "b": FunctionParameter(type="number", description="Second number"),
        },
    )
    assert func_item.name == "add"
    assert func_item.description == "Add a and b"
    assert func_item.auto_call is True
    assert func_item.token_count == 62
    assert func_item.required == ["a", "b"]


def test_init_dict_params():
    func_item = FunctionItem(
        method=lambda a, b: a + b,
        name="add",
        description="Add a and b",
        params={
            "a": {"type": "number", "description": "First number"},
            "b": {"type": "number", "description": "Second number"},
        },
    )
    assert func_item.name == "add"
    assert func_item.description == "Add a and b"
    assert func_item.auto_call is True
    assert func_item.token_count == 62
    assert func_item.required == ["a", "b"]


def test_init_token_override():
    func_item = FunctionItem(
        method=lambda a, b: a + b,
        name="add",
        description="Add a and b",
        params={
            "a": {"type": "number", "description": "First number"},
            "b": {"type": "number", "description": "Second number"},
        },
        token_count=50,
    )
    assert func_item.token_count == 50


def test_init_required_override():
    func_item = FunctionItem(
        method=lambda a, b: a + b,
        name="add",
        description="Add a and b",
        params={
            "a": {"type": "number", "description": "First number"},
            "b": {"type": "number", "description": "Second number"},
        },
        required=["a"],
    )
    assert func_item.required == ["a"]


def test_init_name_validation():
    with pytest.raises(ValueError):
        FunctionItem(
            method=lambda: None,
            name="Name with Spaces",
            description="Add a and b",
            params={},
        )


def test_func_item_call():
    func_item = FunctionItem(
        method=lambda a, b: a + b,
        name="add",
        description="Add a and b",
        params={
            "a": {"type": "number", "description": "First number"},
            "b": {"type": "number", "description": "Second number"},
        },
        token_count=50,
    )
    assert func_item.call_method(a=1, b=2) == 3

    method = func_item.get_call_method(a=1, b=2)
    assert method() == 3


def test_func_item_call_arg_enforcement():
    func_item = FunctionItem(
        method=lambda a, b, f=0: a + b + f,
        name="add",
        description="Add a and b",
        params={
            "a": {
                "type": "number",
                "description": "First number",
                "enum": [1, 2, 3],
            },
            "b": {"type": "number", "description": "Second number"},
            "f": {
                "type": "number",
                "description": "Optional Third number",
                "enum": [0, 1],
            },
        },
        token_count=50,
        required=["a", "b"],
    )
    assert func_item.call_method(a=1, b=2) == 3
    assert func_item.call_method(a="1", b=2) == 3

    with pytest.raises(ValueError) as e:
        func_item.call_method(a=4, b=2)
    assert "Invalid value 4 for a" in str(e.value)

    with pytest.raises(ValueError):
        func_item.call_method(a="bad", b=2)

    with pytest.raises(ValueError) as e:
        func_item.call_method(a=1, c=2)
    assert "Invalid param c" in str(e.value)


def test_func_item_serialize():
    func_item = FunctionItem(
        method=lambda a, b: a + b,
        name="add",
        description="Add a and b",
        params={
            "a": {"type": "number", "description": "First number"},
            "b": {"type": "number", "description": "Second number"},
        },
        token_count=50,
    )
    json_fi = func_item.model_dump_json()
    rebuilt_fi = FunctionItem.model_validate_json(json_fi)

    assert func_item.name == rebuilt_fi.name
    assert func_item.description == rebuilt_fi.description
    assert func_item.params == rebuilt_fi.params
    assert func_item.token_count == rebuilt_fi.token_count
    assert func_item.required == rebuilt_fi.required
    assert func_item.auto_call == rebuilt_fi.auto_call
    assert func_item.tags == rebuilt_fi.tags
    assert func_item.call_method(a=1, b=2) == rebuilt_fi.call_method(a=1, b=2)
