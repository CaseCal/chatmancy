# chatmancy.agent.gpt package

## Submodules

## chatmancy.agent.gpt.agent module

### *class* chatmancy.agent.gpt.agent.GPTAgent(name, desc, model, system_prompt='You are a helpful chat agent.', history=None, token_settings=None, model_max_tokens=None)

Bases: [`Agent`](chatmancy.agent.md#chatmancy.agent.base.Agent)

Agent class for generating chat responses using GPT

* **Parameters:**
  * **name** (*str*) – The name of the agent.
  * **desc** (*str*) – A description of the agent.
  * **model** (*str*) – The name of the OpenAI model to use.
  * **system_prompt** (*str*) – The prompt to use when generating system responses.
  * **history** (*List* *[**str* *]*  *|* [*HistoryGenerator*](chatmancy.agent.md#chatmancy.agent.history.HistoryGenerator)) – A generator to add a history prefix to all calls to the agent.
  * **token_settings** ([*TokenSettings*](chatmancy.agent.md#chatmancy.agent.base.TokenSettings) *|* *dict*) – Settings for the token generation.
  * **model_max_tokens** (*int*) – The maximum number of tokens to generate for the model.
    Required if the passed model is not recorded in GPTModelHandler.

## chatmancy.agent.gpt.history module

### *class* chatmancy.agent.gpt.history.GPTHistoryManager(system_message, generator, max_prefix_tokens=None)

Bases: [`HistoryManager`](chatmancy.agent.md#chatmancy.agent.history.HistoryManager)

* **Parameters:**
  * **system_message** ([*Message*](chatmancy.message.md#chatmancy.message.message.Message)) – 
  * **generator** (*List* *[**str* *]*  *|* [*HistoryGenerator*](chatmancy.agent.md#chatmancy.agent.history.HistoryGenerator)) – 
  * **max_prefix_tokens** (*int*) – 

## chatmancy.agent.gpt.model module

### *class* chatmancy.agent.gpt.model.GPTModelHandler(model, max_tokens=None, agent_name='assistant', \*\*kwargs)

Bases: [`ModelHandler`](chatmancy.agent.md#chatmancy.agent.model.ModelHandler)

* **Parameters:**
  * **model** (*str*) – 
  * **max_tokens** (*int*) – 
  * **agent_name** (*str*) – 

#### call_function(history, function_item)

Force the agent to call a given funuction

* **Parameters:**
  * **history** ([*MessageQueue*](chatmancy.message.md#chatmancy.message.message.MessageQueue)) – The message history.
  * **function_item** ([*FunctionItem*](chatmancy.function.md#chatmancy.function.function_item.FunctionItem)) – The function to call.
* **Returns:**
  The parsed response from the OpenAI API.

#### get_completion(\*\*kwargs)

Generates a chatbot response given a message history and optional functions.

* **Parameters:**
  * **history** ([*MessageQueue*](chatmancy.message.md#chatmancy.message.message.MessageQueue)) – The message history to generate a response from.
  * **functions** (*List* *[*[*FunctionItem*](chatmancy.function.md#chatmancy.function.function_item.FunctionItem) *]* *,* *optional*) – A list of FunctionItem objects
    to use for generating the response. Defaults to None.
* **Returns:**
  The generated chatbot response.
* **Return type:**
  ChatCompletion

## Module contents
