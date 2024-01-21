# chatmancy.agent package

## Subpackages

* [chatmancy.agent.gpt package](chatmancy.agent.gpt.md)
  * [Submodules](chatmancy.agent.gpt.md#submodules)
  * [chatmancy.agent.gpt.agent module](chatmancy.agent.gpt.md#module-chatmancy.agent.gpt.agent)
    * [`GPTAgent`](chatmancy.agent.gpt.md#chatmancy.agent.gpt.agent.GPTAgent)
  * [chatmancy.agent.gpt.history module](chatmancy.agent.gpt.md#module-chatmancy.agent.gpt.history)
    * [`GPTHistoryManager`](chatmancy.agent.gpt.md#chatmancy.agent.gpt.history.GPTHistoryManager)
  * [chatmancy.agent.gpt.model module](chatmancy.agent.gpt.md#module-chatmancy.agent.gpt.model)
    * [`GPTModelHandler`](chatmancy.agent.gpt.md#chatmancy.agent.gpt.model.GPTModelHandler)
      * [`GPTModelHandler.call_function()`](chatmancy.agent.gpt.md#chatmancy.agent.gpt.model.GPTModelHandler.call_function)
      * [`GPTModelHandler.get_completion()`](chatmancy.agent.gpt.md#chatmancy.agent.gpt.model.GPTModelHandler.get_completion)
  * [Module contents](chatmancy.agent.gpt.md#module-chatmancy.agent.gpt)

## Submodules

## chatmancy.agent module

### *class* chatmancy.agent.base.Agent(name, desc, history=None, token_settings=None, \*\*kwargs)

Bases: `ABC`

Agent base class for generating chat responses.

* **Parameters:**
  * **name** (*str*) – 
  * **desc** (*str*) – 
  * **history** (*List* *[**str* *]*  *|* [*HistoryGenerator*](#chatmancy.agent.history.HistoryGenerator)) – 
  * **token_settings** ([*TokenSettings*](#chatmancy.agent.base.TokenSettings) *|* *dict*) – 

#### call_function(input_message, history, context, function_item)

Force the agent to call a given funuction

* **Parameters:**
  * **input_message** ([*Message*](chatmancy.message.md#chatmancy.message.message.Message)) – The input message to respond to.
  * **history** ([*MessageQueue*](chatmancy.message.md#chatmancy.message.message.MessageQueue)) – The history of the conversation.
  * **function_item** ([*FunctionItem*](chatmancy.function.md#chatmancy.function.function_item.FunctionItem)) – The function to call.
  * **context** (*Dict*) – 
* **Returns:**
  The parsed response from the OpenAI API.
* **Return type:**
  [*FunctionRequestMessage*](chatmancy.function.md#chatmancy.function.function_message.FunctionRequestMessage)

#### get_response_message(\*\*kwargs)

#### give_function_response(history)

* **Parameters:**
  **history** ([*MessageQueue*](chatmancy.message.md#chatmancy.message.message.MessageQueue)) – 
* **Return type:**
  [*Message*](chatmancy.message.md#chatmancy.message.message.Message)

### *class* chatmancy.agent.base.TokenSettings(max_prefix_tokens: int | None = None, max_function_tokens: int | None = None, min_response_tokens: int = 750)

Bases: `object`

* **Parameters:**
  * **max_prefix_tokens** (*int* *|* *None*) – 
  * **max_function_tokens** (*int* *|* *None*) – 
  * **min_response_tokens** (*int*) – 

#### max_function_tokens *: int | None* *= None*

#### max_prefix_tokens *: int | None* *= None*

#### min_response_tokens *: int* *= 750*

<a id="module-chatmancy.agent.functions"></a>

### *class* chatmancy.agent.functions.FunctionHandler(max_tokens=None, \*\*kwargs)

Bases: `object`

* **Parameters:**
  **max_tokens** (*int*) – 

#### select_functions(functions, input_message, history=None, context=None)

Returns a list of functions that are applicable to the given
input message, history, and context.

* **Parameters:**
  * **functions** (*List* *[*[*FunctionItem*](chatmancy.function.md#chatmancy.function.function_item.FunctionItem) *]*) – A list of FunctionItem objects representing
    the available functions.
  * **input_message** ([*Message*](chatmancy.message.md#chatmancy.message.message.Message)) – The input message to be processed.
  * **history** ([*MessageQueue*](chatmancy.message.md#chatmancy.message.message.MessageQueue)) – A lMessageQueue representing the
    conversation history.
  * **context** (*Dict* *[**str* *,* *Any* *]*) – A dictionary containing contextual
    information about the conversation.
* **Returns:**
  A list of FunctionItem objects representing the
  : applicable functions.
* **Return type:**
  List[[FunctionItem](chatmancy.function.md#chatmancy.function.function_item.FunctionItem)]

<a id="module-chatmancy.agent.history"></a>

### *class* chatmancy.agent.history.HistoryGenerator

Bases: `ABC`

Abstract Base Class for generating a history.

#### create_history(\*\*kwargs)

### *class* chatmancy.agent.history.HistoryManager(generator, max_prefix_tokens=None)

Bases: `object`

Manages the history of messages in a conversation.

* **Parameters:**
  * **generator** (*List* *[**str* *]*  *|* [*HistoryGenerator*](#chatmancy.agent.history.HistoryGenerator)) – The generator used to
    create the history.
  * **max_prefix_tokens** (*int* *,* *optional*) – The maximum number of tokens to include in
    the prefix. Defaults to None.
* **Raises:**
  **TypeError** – If the generator is not a list of statements or a HistoryGenerator.

#### max_prefix_tokens

The maximum number of tokens to include in the prefix.

* **Type:**
  int

#### generator

The generator used to create the history.

* **Type:**
  [HistoryGenerator](#chatmancy.agent.history.HistoryGenerator)

#### create_history()

Creates the history based on the
input message, context, and maximum number of tokens.

#### create_history(\*\*kwargs)

### *class* chatmancy.agent.history.StaticHistoryGenerator(statements, \*\*kwargs)

Bases: [`HistoryGenerator`](#chatmancy.agent.history.HistoryGenerator)

A class to generate a static history from a given list of statements.

* **Parameters:**
  **statements** (*List* *[**str* *]*) – 

#### create_history(\*\*kwargs)

<a id="module-chatmancy.agent.model"></a>

### *class* chatmancy.agent.model.ModelHandler(max_tokens, \*\*kwargs)

Bases: `ABC`

Abstract base class for ModelHandlers.
ModelHandlers convert Messages and Functions into the correct format
for an LLM API or model, and convert responses from the model into Messages
and FunctionRequestMessages.

* **Parameters:**
  **max_tokens** (*int*) – 

#### *abstract* call_function(history, function_item)

Force the agent to call a given funuction

* **Parameters:**
  * **history** ([*MessageQueue*](chatmancy.message.md#chatmancy.message.message.MessageQueue)) – The message history.
  * **function_item** ([*FunctionItem*](chatmancy.function.md#chatmancy.function.function_item.FunctionItem)) – The function to call.
* **Returns:**
  The parsed response from the OpenAI API.
* **Return type:**
  [*FunctionRequestMessage*](chatmancy.function.md#chatmancy.function.function_message.FunctionRequestMessage)

#### *abstract* get_completion(history, functions=None)

Generates a chatbot response given a message history and optional functions.

* **Parameters:**
  * **history** ([*MessageQueue*](chatmancy.message.md#chatmancy.message.message.MessageQueue)) – The message history to generate a response from.
  * **functions** (*List* *[*[*FunctionItem*](chatmancy.function.md#chatmancy.function.function_item.FunctionItem) *]* *,* *optional*) – A list of FunctionItem objects
    to use for generating the response. Defaults to None.
* **Returns:**
  The generated chatbot response.
* **Return type:**
  ChatCompletion

#### max_tokens *: int*
