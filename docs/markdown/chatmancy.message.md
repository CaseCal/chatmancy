# chatmancy.message package

## Submodules

## chatmancy.message.message module

### *class* chatmancy.message.message.AgentMessage(content, token_count=None, agent_name='assistant', \*, sender)

Bases: [`Message`](#chatmancy.message.message.Message)

* **Parameters:**
  * **content** (*str*) – 
  * **token_count** (*int* *|* *None*) – 
  * **agent_name** (*str*) – 
  * **sender** (*str*) – 

#### agent_name *: str*

#### model_config *: ClassVar[ConfigDict]* *= {}*

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### model_fields *: ClassVar[dict[str, FieldInfo]]* *= {'agent_name': FieldInfo(annotation=str, required=False, default='assistant'), 'content': FieldInfo(annotation=str, required=True), 'sender': FieldInfo(annotation=str, required=True), 'token_count': FieldInfo(annotation=Union[int, NoneType], required=False, validate_default=True)}*

Metadata about the fields defined on the model,
mapping of field names to [FieldInfo][pydantic.fields.FieldInfo].

This replaces Model._\_fields_\_ from Pydantic V1.

### *class* chatmancy.message.message.Message(\*, sender, content, token_count=None)

Bases: `BaseModel`

A class that represents a message.

* **Parameters:**
  * **sender** (*str*) – 
  * **content** (*str*) – 
  * **token_count** (*int* *|* *None*) – 

#### *classmethod* compute_token_count(v, v_info)

* **Parameters:**
  * **v** (*Any*) – 
  * **v_info** (*ValidationInfo*) – 

#### content *: str*

#### model_config *: ClassVar[ConfigDict]* *= {}*

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### model_fields *: ClassVar[dict[str, FieldInfo]]* *= {'content': FieldInfo(annotation=str, required=True), 'sender': FieldInfo(annotation=str, required=True), 'token_count': FieldInfo(annotation=Union[int, NoneType], required=False, validate_default=True)}*

Metadata about the fields defined on the model,
mapping of field names to [FieldInfo][pydantic.fields.FieldInfo].

This replaces Model._\_fields_\_ from Pydantic V1.

#### sender *: str*

#### token_count *: int | None*

### *class* chatmancy.message.message.MessageQueue(iterable=None)

Bases: `deque`

#### append(message)

Add an element to the right side of the deque.

#### appendleft(message)

Add an element to the left side of the deque.

#### copy()

Create a shallow copy of the MessageQueue.

# Return
A new MessageQueue that’s a copy of the original.

#### extend(messages)

Extend the right side of the deque with elements from the iterable

#### get_last_n_messages(n, exclude_types=())

Return the most recent n messages

# Return
List of messages

* **Parameters:**
  **exclude_types** (*Tuple* *[**Type* *]*) – 
* **Return type:**
  *List*[[*Message*](#chatmancy.message.message.Message)]

#### get_last_n_tokens(n, exclude_types=())

Return the most recent messages, up to a total token count of n.

# Return
List of messages whose total token count is less than n.

* **Parameters:**
  **exclude_types** (*Tuple* *[**Type* *]*) – 
* **Return type:**
  *List*[[*Message*](#chatmancy.message.message.Message)]

#### *property* token_count

### *class* chatmancy.message.message.UserMessage(content, token_count=None)

Bases: [`Message`](#chatmancy.message.message.Message)

* **Parameters:**
  * **content** (*str*) – 
  * **token_count** (*int*) – 

#### model_config *: ClassVar[ConfigDict]* *= {}*

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### model_fields *: ClassVar[dict[str, FieldInfo]]* *= {'content': FieldInfo(annotation=str, required=True), 'sender': FieldInfo(annotation=str, required=True), 'token_count': FieldInfo(annotation=Union[int, NoneType], required=False, validate_default=True)}*

Metadata about the fields defined on the model,
mapping of field names to [FieldInfo][pydantic.fields.FieldInfo].

This replaces Model._\_fields_\_ from Pydantic V1.

## Module contents
