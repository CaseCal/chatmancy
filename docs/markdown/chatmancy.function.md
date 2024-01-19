# chatmancy.function package

## Submodules

## chatmancy.function.function_item module

### *class* chatmancy.function.function_item.FunctionItem(\*, method, name, description, params, required=None, auto_call=True, tags=None, token_count=None)

Bases: `BaseModel`

A class that represents a function item. This class is used for
passing function arguments to GPTAgents

* **Parameters:**
  * **method** (*Callable*) – 
  * **name** (*str*) – 
  * **description** (*str*) – 
  * **params** (*Dict* *[**str* *,* [*FunctionParameter*](#chatmancy.function.function_item.FunctionParameter) *]*) – 
  * **required** (*List* *[**str* *]*  *|* *None*) – 
  * **auto_call** (*bool*) – 
  * **tags** (*Set* *[**str* *]*) – 
  * **token_count** (*int* *|* *None*) – 

#### method

A callable function or method that should be invoked.

* **Type:**
  Callable

#### name

The name of the function.

* **Type:**
  str

#### description

A brief description of what the function does.

* **Type:**
  str

#### params

A dictionary that maps parameter names to their
specifications. Each specification is another dictionary that includes
“type” and “description” fields for the parameter.

* **Type:**
  Dict[str, dict]

#### required

A list of required parameter names. If not
provided, defaults to all parameters being required.

* **Type:**
  Optional[List[str]]

#### auto_call

If True, the function will be automatically invoked when its
name is called. If False, a FunctionRequest object is returned instead.
Defaults to True.

* **Type:**
  bool

#### to_dict()

Converts the FunctionItem to a dictionary in JSON object format.

#### get_call_method(\*\*kwargs)

Partially applies the provided kwargs to the method
and returns a callable that only needs the remaining arguments.

#### auto_call *: bool*

#### call_method(\*\*kwargs)

#### *classmethod* compute_token_count(v, v_info)

* **Parameters:**
  * **v** (*Any*) – 
  * **v_info** (*ValidationInfo*) – 

#### description *: str*

#### *classmethod* deserialize_method(v, v_info)

* **Parameters:**
  **v_info** (*ValidationInfo*) – 

#### get_call_method(\*\*kwargs)

#### method *: Callable*

#### model_config *: ClassVar[ConfigDict]* *= {'arbitrary_types_allowed': True, 'validate_assignment': True}*

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### model_fields *: ClassVar[dict[str, FieldInfo]]* *= {'auto_call': FieldInfo(annotation=bool, required=False, default=True), 'description': FieldInfo(annotation=str, required=True), 'method': FieldInfo(annotation=Callable, required=True), 'name': FieldInfo(annotation=str, required=True), 'params': FieldInfo(annotation=Dict[str, FunctionParameter], required=True), 'required': FieldInfo(annotation=Union[List[str], NoneType], required=False, validate_default=True), 'tags': FieldInfo(annotation=Set[str], required=False, default_factory=set), 'token_count': FieldInfo(annotation=Union[int, NoneType], required=False, validate_default=True)}*

Metadata about the fields defined on the model,
mapping of field names to [FieldInfo][pydantic.fields.FieldInfo].

This replaces Model._\_fields_\_ from Pydantic V1.

#### name *: str*

#### params *: Dict[str, [FunctionParameter](#chatmancy.function.function_item.FunctionParameter)]*

#### required *: List[str] | None*

#### serialize_method(method)

#### *classmethod* set_required(v, v_info)

* **Parameters:**
  **v_info** (*ValidationInfo*) – 

#### tags *: Set[str]*

#### token_count *: int | None*

#### *classmethod* validate_name_format(v, v_info)

Ensure name in ‘^[

```
a-zA-Z0-9_
```

-]{1,64}$’ format

* **Parameters:**
  * **v** (*str*) – 
  * **v_info** (*ValidationInfo*) – 

### *class* chatmancy.function.function_item.FunctionItemFactory(params=None, tags=None)

Bases: `object`

* **Parameters:**
  * **params** (*Dict* *[**str* *,* [*FunctionParameter*](#chatmancy.function.function_item.FunctionParameter) *]*) – 
  * **tags** (*List* *[**str* *]*) – 

#### create_function_item(method, name, description, params=None, required=None, custom_params=None, tags=None, auto_call=True)

* **Parameters:**
  * **method** (*str*) – 
  * **name** (*str*) – 
  * **description** (*str*) – 
  * **params** (*List* *[**str* *]*  *|* *None*) – 
  * **required** (*List* *[**str* *]*  *|* *None*) – 
  * **custom_params** (*Dict* *[**str* *,* *Dict* *[**str* *,* *str* *|* *List* *[**str* *]* *]* *]*  *|* *None*) – 
  * **tags** (*List* *[**str* *]*  *|* *None*) – 
  * **auto_call** (*bool*) – 
* **Return type:**
  [*FunctionItem*](#chatmancy.function.function_item.FunctionItem)

#### validate_params(params)

* **Parameters:**
  **params** (*Dict* *[**str* *,* *Dict* *[**str* *,* *str* *|* *List* *[**str* *]* *]* *]*) – 

### *class* chatmancy.function.function_item.FunctionParameter(\*, type='string', description, enum=None)

Bases: `BaseModel`

A class that represents a function parameter. This class is used for
passing function arguments to GPTAgents

* **Parameters:**
  * **type** (*str*) – 
  * **description** (*str*) – 
  * **enum** (*List* *[**str* *|* *int* *]*  *|* *None*) – 

#### type

The type of the parameter.

* **Type:**
  str

#### description

A brief description of what the parameter does.

* **Type:**
  str

#### enum

A list of possible values for the parameter.

* **Type:**
  Optional[List[str]]

#### description *: str*

#### enum *: List[str | int] | None*

#### model_config *: ClassVar[ConfigDict]* *= {}*

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### model_fields *: ClassVar[dict[str, FieldInfo]]* *= {'description': FieldInfo(annotation=str, required=True), 'enum': FieldInfo(annotation=Union[List[Union[str, int]], NoneType], required=False), 'type': FieldInfo(annotation=str, required=False, default='string')}*

Metadata about the fields defined on the model,
mapping of field names to [FieldInfo][pydantic.fields.FieldInfo].

This replaces Model._\_fields_\_ from Pydantic V1.

#### type *: str*

## chatmancy.function.function_message module

### *class* chatmancy.function.function_message.FunctionRequestMessage(requests, \*, sender, content, token_count=None, agent_name='assistant')

Bases: [`AgentMessage`](chatmancy.message.md#chatmancy.message.message.AgentMessage)

A class that represents a message.

* **Parameters:**
  * **requests** (*List* *[* *\_FunctionRequest* *]*) – 
  * **sender** (*str*) – 
  * **content** (*str*) – 
  * **token_count** (*int* *|* *None*) – 
  * **agent_name** (*str*) – 

#### *property* approvals_required

#### create_function_requests(v)

Cast dicts to function requests

#### create_responses(approved_ids=None)

* **Parameters:**
  **approved_ids** (*List* *[**str* *]*  *|* *None*) – 
* **Return type:**
  *List*[[*FunctionResponseMessage*](#chatmancy.function.function_message.FunctionResponseMessage)]

#### model_config *: ClassVar[ConfigDict]* *= {}*

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### model_fields *: ClassVar[dict[str, FieldInfo]]* *= {'agent_name': FieldInfo(annotation=str, required=False, default='assistant'), 'content': FieldInfo(annotation=str, required=True), 'requests': FieldInfo(annotation=List[_FunctionRequest], required=True), 'sender': FieldInfo(annotation=str, required=True), 'token_count': FieldInfo(annotation=Union[int, NoneType], required=False, validate_default=True)}*

Metadata about the fields defined on the model,
mapping of field names to [FieldInfo][pydantic.fields.FieldInfo].

This replaces Model._\_fields_\_ from Pydantic V1.

#### requests *: List[\_FunctionRequest]*

### *class* chatmancy.function.function_message.FunctionResponseMessage(func_name, func_id, \*, sender, content, token_count=None)

Bases: [`Message`](chatmancy.message.md#chatmancy.message.message.Message)

Represents a response message from a function.

* **Parameters:**
  * **func_name** (*str*) – 
  * **func_id** (*str*) – 
  * **sender** (*str*) – 
  * **content** (*str*) – 
  * **token_count** (*int* *|* *None*) – 

#### func_name

The name of the function.

* **Type:**
  str

#### content

The content of the message.

* **Type:**
  str

#### token_count

The number of tokens in the message.

* **Type:**
  int

#### sender

The sender of the message. Defaults to ‘function’

* **Type:**
  str

#### func_id *: str*

#### func_name *: str*

#### model_config *: ClassVar[ConfigDict]* *= {}*

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### model_fields *: ClassVar[dict[str, FieldInfo]]* *= {'content': FieldInfo(annotation=str, required=True), 'func_id': FieldInfo(annotation=str, required=True), 'func_name': FieldInfo(annotation=str, required=True), 'sender': FieldInfo(annotation=str, required=True), 'token_count': FieldInfo(annotation=Union[int, NoneType], required=False, validate_default=True)}*

Metadata about the fields defined on the model,
mapping of field names to [FieldInfo][pydantic.fields.FieldInfo].

This replaces Model._\_fields_\_ from Pydantic V1.

## chatmancy.function.generator module

### *class* chatmancy.function.generator.FunctionItemGenerator

Bases: `ABC`

#### generate_functions(input_message, history, context)

* **Parameters:**
  * **input_message** ([*Message*](chatmancy.message.md#chatmancy.message.message.Message)) – 
  * **history** ([*MessageQueue*](chatmancy.message.md#chatmancy.message.message.MessageQueue)) – 
  * **context** (*Dict* *[**str* *,* *str* *]*) – 
* **Return type:**
  *List*[[*FunctionItem*](#chatmancy.function.function_item.FunctionItem)]

### *class* chatmancy.function.generator.KeywordSortedMixin(search_depth=5, decay_rate=0.5, relative_keyword_weighting=False, \*\*kwargs)

Bases: [`FunctionItemGenerator`](#chatmancy.function.generator.FunctionItemGenerator)

* **Parameters:**
  * **search_depth** (*int*) – 
  * **decay_rate** (*float*) – 
  * **relative_keyword_weighting** (*bool*) – 

#### generate_functions(input_message, history, context)

* **Parameters:**
  * **input_message** ([*Message*](chatmancy.message.md#chatmancy.message.message.Message)) – 
  * **history** ([*MessageQueue*](chatmancy.message.md#chatmancy.message.message.MessageQueue)) – 
  * **context** (*Dict* *[**str* *,* *str* *]*) – 
* **Return type:**
  *List*[[*FunctionItem*](#chatmancy.function.function_item.FunctionItem)]

### *class* chatmancy.function.generator.StaticFunctionItemGenerator(functions)

Bases: [`FunctionItemGenerator`](#chatmancy.function.generator.FunctionItemGenerator)

* **Parameters:**
  **functions** (*List* *[*[*FunctionItem*](#chatmancy.function.function_item.FunctionItem) *]*) – 

#### generate_functions(input_message, history, context)

* **Parameters:**
  * **input_message** ([*Message*](chatmancy.message.md#chatmancy.message.message.Message)) – 
  * **history** ([*MessageQueue*](chatmancy.message.md#chatmancy.message.message.MessageQueue)) – 
  * **context** (*Dict* *[**str* *,* *str* *]*) – 
* **Return type:**
  *List*[[*FunctionItem*](#chatmancy.function.function_item.FunctionItem)]

## Module contents
