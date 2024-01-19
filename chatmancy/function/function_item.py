import base64
from functools import partial
import json
import re
import dill as pickle
from typing import Any, Callable, List, Dict, Optional, Set, Union

from pydantic import BaseModel, Field, ValidationInfo, field_serializer, field_validator
import tiktoken

from ..logging import trace


class FunctionParameter(BaseModel):
    """
    A class that represents a function parameter. This class is used for
    passing function arguments to GPTAgents

    Attributes:
        type (str): The type of the parameter.
        description (str): A brief description of what the parameter does.
        enum (Optional[List[str]]): A list of possible values for the parameter.
    """

    type: str = "string"
    description: str
    enum: Optional[List[(str | int)]] = None


class FunctionItem(BaseModel):
    """
    A class that represents a function item. This class is used for
    passing function arguments to GPTAgents

    Attributes:
        method (Callable): A callable function or method that should be invoked.
        name (str): The name of the function.
        description (str): A brief description of what the function does.
        params (Dict[str, dict]): A dictionary that maps parameter names to their
            specifications. Each specification is another dictionary that includes
            "type" and "description" fields for the parameter.
        required (Optional[List[str]]): A list of required parameter names. If not
            provided, defaults to all parameters being required.
        auto_call (bool): If True, the function will be automatically invoked when its
            name is called. If False, a FunctionRequest object is returned instead.
            Defaults to True.

    Methods:
        to_dict(): Converts the FunctionItem to a dictionary in JSON object format.
        get_call_method(**kwargs): Partially applies the provided kwargs to the method
            and returns a callable that only needs the remaining arguments.
    """

    method: Callable
    name: str
    description: str
    params: Dict[str, FunctionParameter]
    required: Optional[List[str]] = Field(default=None, validate_default=True)
    auto_call: bool = True
    tags: Set[str] = Field(default_factory=set)
    token_count: Optional[int] = Field(validate_default=True, default=None)

    model_config = {
        "validate_assignment": True,
        "arbitrary_types_allowed": True,
    }

    @field_validator("name", mode="after")
    def validate_name_format(cls, v: str, v_info: ValidationInfo):
        """
        Ensure name in '^[a-zA-Z0-9_-]{1,64}$' format
        """
        r = r"^[a-zA-Z0-9_-]{1,64}$"
        if not re.match(r, v):
            raise ValueError(f"Invalid name format for {v}, must match {r}")
        return v

    @field_validator(
        "token_count",
        mode="after",
    )
    def compute_token_count(cls, v: Any, v_info: ValidationInfo):
        if v is not None:
            return v
        enc = tiktoken.encoding_for_model("gpt-4")

        # Check required params and encode
        relevant_content_keys = ["name", "description", "params", "required"]
        relevant_content = {}
        for k in relevant_content_keys:
            if k in v_info.data:
                relevant_content[k] = v_info.data[k]
            else:
                raise ValueError(f"Missing required field {k}")
        relevant_content["params"] = {
            k: v.model_dump_json() for k, v in relevant_content["params"].items()
        }

        relevant_content = json.dumps(relevant_content)
        tk = len(enc.encode(relevant_content))
        return tk

    @field_validator("required", mode="before")
    def set_required(cls, v, v_info: ValidationInfo):
        return v if v is not None else list(v_info.data.get("params", {}).keys())

    @field_validator("method", mode="before")
    def deserialize_method(cls, v, v_info: ValidationInfo):
        if isinstance(v, str):
            return pickle.loads(base64.b64decode(v))
        return v

    @field_serializer("method")
    def serialize_method(self, method):
        serialized_data = pickle.dumps(method)
        base64_encoded_data = base64.b64encode(serialized_data).decode("utf-8")
        return base64_encoded_data

    def get_call_method(self, **kwargs):
        result = partial(self.method, **kwargs)
        return result

    @trace(name="FunctionItem.call_method")
    def call_method(self, **kwargs) -> str:
        # Validate
        validated_args = self._validate_call(kwargs)
        return self.method(**validated_args)

    def _validate_call(self, kwargs) -> Dict[str, Any]:
        for arg_name, arg_value in kwargs.items():
            # param exists
            if arg_name not in self.params:
                msg = f"Invalid param {arg_name}, must be in {self.params.keys()}"
                raise ValueError(msg)
            enum = self.params[arg_name].enum

            # param type
            if self.params[arg_name].type == "number":
                if not isinstance(arg_value, (int, float)):
                    try:
                        arg_value = float(arg_value)
                        kwargs[arg_name] = arg_value
                    except Exception:
                        raise ValueError(
                            (
                                f"Invalid value {arg_value} for {arg_name}, "
                                "must be a number"
                            )
                        )

            # param Enum
            if enum and arg_value not in enum:
                raise ValueError(
                    f"Invalid value {arg_value} for {arg_name}, must be in {enum}"
                )

        return kwargs


class FunctionItemFactory:
    def __init__(
        self,
        params: Dict[str, FunctionParameter] = None,
        tags: List[str] = None,
    ) -> None:
        self._params = {}
        self._params.update(params or {})
        self.validate_params(self._params)

        self._tags = tags or []

    def validate_params(self, params: Dict[str, Dict[str, Union[str, List[str]]]]):
        for param_name, param_value in params.items():
            # Name is str
            if not isinstance(param_name, str):
                raise ValueError(f"Invalid param name {param_name}, must be a string")

            # Value is param
            self._params[param_name] = FunctionParameter(**param_value)

    def create_function_item(
        self,
        method: str,
        name: str,
        description: str,
        params: List[str] = None,
        required: List[str] = None,
        custom_params: Dict[str, Dict[str, Union[str, List[str]]]] = None,
        tags: List[str] = None,
        auto_call: bool = True,
    ) -> FunctionItem:
        # Prepare params
        if params is None:
            params = []
        try:
            params = {param: self._params[param] for param in params}
        except KeyError:
            raise ValueError(
                f"Invalid param detected, must be in {self._params.keys()}"
            )
        if custom_params:
            self.validate_params(custom_params)
            params.update(custom_params)
        if required is None:
            required = list(params.keys())

        # Prepare tags
        if tags is None:
            tags = []

        return FunctionItem(
            method=method,
            name=name,
            description=description,
            params=params,
            required=required,
            auto_call=auto_call,
            tags=[*self._tags, *tags],
        )
