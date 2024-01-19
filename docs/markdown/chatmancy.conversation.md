# chatmancy.conversation package

## Submodules

## chatmancy.conversation.context_manager module

### *class* chatmancy.conversation.context_manager.AgentContextManager(name, context_item, model='gpt-4')

Bases: [`ContextManager`](#chatmancy.conversation.context_manager.ContextManager)

A context manager that determines context using an LLM agent

* **Parameters:**
  * **name** (*str*) – 
  * **context_item** ([*ContextItem*](#chatmancy.conversation.context_manager.ContextItem) *|* *Dict*) – 
  * **model** (*str*) – 

#### name

The name of the context.

* **Type:**
  str

#### context_items

A list of context items.

* **Type:**
  List[[ContextItem](#chatmancy.conversation.context_manager.ContextItem)]

#### model_handler

A model handler for the context.

* **Type:**
  [ModelHandler](chatmancy.agent.md#chatmancy.agent.model.ModelHandler)

### get_context_updates(history

MessageQueue) -> Dict:
Analyzes the message history and updates the current context.

### *class* chatmancy.conversation.context_manager.ContextItem(\*, name, description, type='string', valid_values=None)

Bases: `BaseModel`

* **Parameters:**
  * **name** (*str*) – 
  * **description** (*str*) – 
  * **type** (*str*) – 
  * **valid_values** (*List* *[**str* *]*  *|* *None*) – 

#### description *: str*

#### model_config *: ClassVar[ConfigDict]* *= {}*

Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].

#### model_fields *: ClassVar[dict[str, FieldInfo]]* *= {'description': FieldInfo(annotation=str, required=True), 'name': FieldInfo(annotation=str, required=True), 'type': FieldInfo(annotation=str, required=False, default='string'), 'valid_values': FieldInfo(annotation=Union[List[str], NoneType], required=False)}*

Metadata about the fields defined on the model,
mapping of field names to [FieldInfo][pydantic.fields.FieldInfo].

This replaces Model._\_fields_\_ from Pydantic V1.

#### name *: str*

#### to_function_item()

Converts the ContextItem to a dictionary fitting JSON schema object specs.

* **Returns:**
  A dictionary representing the JSON schema object.
* **Return type:**
  Dict

#### type *: str*

#### valid_values *: List[str] | None*

### *class* chatmancy.conversation.context_manager.ContextManager(name, keys=None)

Bases: `ABC`

A class that manages the context of a conversation.

* **Parameters:**
  * **name** (*str*) – 
  * **keys** (*List* *[**str* *]*  *|* *None*) – 

#### name

The name of the context manager.

* **Type:**
  str

#### get_context_updates(history, current_context)

Analyzes the message history and updates the current context.

* **Parameters:**
  * **history** ([*MessageQueue*](chatmancy.message.md#chatmancy.message.message.MessageQueue)) – The list of past messages.
  * **current_context** (*Dict*) – The current context.
* **Returns:**
  Updated context.
* **Return type:**
  Dict

#### *property* registered_keys *: List[str]*

Returns:
List[str]: The keys that this context manager is responsible for.

## chatmancy.conversation.conversation module

### *class* chatmancy.conversation.conversation.Conversation(main_agent, opening_prompt='Hello!', context_managers=None, function_generators=None, history=None, name=None, context=None)

Bases: `object`

* **Parameters:**
  * **main_agent** ([*Agent*](chatmancy.agent.md#chatmancy.agent.base.Agent)) – 
  * **opening_prompt** (*str*) – 
  * **context_managers** (*List* *[*[*ContextManager*](#chatmancy.conversation.context_manager.ContextManager) *]*) – 
  * **function_generators** (*List* *[*[*FunctionItemGenerator*](chatmancy.function.md#chatmancy.function.generator.FunctionItemGenerator) *]*) – 
  * **name** (*str*) – 
  * **context** (*Dict* *[**str* *,* *str* *]*) – 

#### *property* context

#### context_managers *: List[[ContextManager](#chatmancy.conversation.context_manager.ContextManager)]*

#### main_agent *: [Agent](chatmancy.agent.md#chatmancy.agent.base.Agent)*

#### send_message(\*\*kwargs)

#### user_message_history *: [MessageQueue](chatmancy.message.md#chatmancy.message.message.MessageQueue)*

## Module contents
