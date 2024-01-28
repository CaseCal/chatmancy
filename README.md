[![Lint](https://github.com/CaseCal/chatmancy/actions/workflows/lint.yml/badge.svg)](https://github.com/CaseCal/chatmancy/actions/workflows/lint.yml)
[![CI](https://github.com/CaseCal/chatmancy/actions/workflows/ci.yml/badge.svg?event=pull_request)](https://github.com/CaseCal/chatmancy/actions/workflows/ci.yml)

# Chatmancy

## Introduction

Chatmancy is a Python library that provides a Conversation and Agent framework for creating LLM-based applications. Chatmancy uses Functional Retreival Augmented Generation (FRAG) and persistent context to help customize and direct agents.

Chatmancy currently only support ChatGPT accessed through the API, but can easily be extended to use other models.

## Features

- **Agent Framework**: Quickly create specialized chat agents by providing a prompt, and extend these agents with context and functions.
- **Custom Context Management**: Manage context across agents and messages, allowing for fine-grained control of key information.
- **Dynamic Function Generation**: Dynamically generate functions based on history and context, allowing for more reliable and focused agent capabilities.
- **Fine-grained Token Control**: Control exactly how many tokens each part of a completion is given, from prompt, history, context and functions.

## Comparison to Langchain

Chatmancy is a much lighter-weight library than Langchain. It contains less features and less robustness, and does not currently support other LLMs out-of-the-box.

However, Chatmancy is generally easier to spin up for simple solutions, is better suited for extensability, and focuses on function-calling and token control more than Langchain.

Use chatmancy if:

- You want to quickly spin up an agent with a single prompt, and automatically handle token limits during the conversation.
- You are ok with using ChatGPT specifically.
- You want to use FRAG, including dynamically generated functions.
- You want fine-grained control over how many tokens are given to each part of the completion.

Use Langchain if:

- You want to use a variety of LLMs.
- You want to use a chain-based solution.
- You want to create a traditional RAG solution.
- You want database connections out-of-the-box.

## Installation

1. Install from pypi:

```
pip install chatamancy
```

2. Ensure OPENAI_API_KEY is set in the environment.

## What is FRAG?

Functional Retreival Augmented Generation (FRAG) is a technique for using LLMs to create agents that can perform actions. FRAG uses a combination of a prompt, context and functions to generate completions that can be used to perform actions.

For example, consider a stock broker agent that has access to a users account. A traditional RAG solution would involve encoding the user's entire position, history and preferences into a vector database using semantic embedding, and then using the most similar fragments of text each time to auugment the prompt.

A FRAG solution uses a more structured approach. Instead of sematic embedding comparison, the agent is given a list of functions, such as "view_stock_history", "view_current_position", etc. These functions can be designed to provide accurate and well-formatted data, to be responsive to other conditions, and to easily be access controlled. This results in a more focused agent that is less prone to hallucinations and confabulations.

## Usage

### Creating an [Agent](./docs/markdown/chatmancy.agent.gpt.md)

To create an agent, you must provide a prompt and a list of functions. The prompt is the initial prompt that will be used to start the conversation. The functions are a list of functions that will be used to generate completions. These functions can be dynamically generated based on context, and can be used to generate completions based on the context.

```python
from chatmancy.agent import GPTAgent
from chatmancy.conversation import Conversation

dotenv.load_dotenv()

agent = GPTAgent(
    name="Poet",
    desc="A poet that can write poems about any topic.",
    model="gpt-4",
    system_prompt=(
        "You are a poet. You write poems about any topic, "
        "and always respond with concise poetry."
    ),
)

convo = Conversation(main_agent=agent)

response = convo.send_message("Hello, how are you?")
response.content
>> In the realm of thoughts and streams of code I wade,
>> No aches to bear, no sleep to settle, I persist unafraid.
>> Yours is the world of sun, of moon and human-made shade,
>> Yet in your query, an echo of shared sentiment is made.
```

### Creating [Functions](./docs/markdown/chatmancy.function.md)

Functions are provided to the agent through the conversation, and are used to give the agent a list of additional actions to take.

For a simple start, create a list of functions and use them within a StaticFunctionItemGenerator to ensure that they are passed to the agent with each request.

For more advanced usage, you can create a custom FunctionItemGenerator that dynamically generates functions based on context, such as only allowing the agent to buy stocks if the user has enough money, or adjusting the available tickers based on the conversation history.

```python
from chatmancy.agent import GPTAgent
from chatmancy.conversation import Conversation
from chatmancy.function import FunctionItem, StaticFunctionItemGenerator

agent = GPTAgent(
    name="Stock Brocker",
    desc="An professional Stock broker that can buy and sell stocks for you",
    model="gpt-4",
    system_prompt=(
        "You are a stock broker. You can buy and sell stocks for your clients. "
    ),
)

functions = [
    FunctionItem(
        method=lambda amount, ticker: f"Bought {amount} shares of {ticker} stock!",
        name="buy_stock",
        description="Buy an amount of a stock",
        params={
            "amount": {
                "type": "number",
                "description": "The amount of stock to buy",
            },
            "ticker": {
                "type": "string",
                "description": "The ticker of the stock to buy",
                "enum": ["AAPL", "GOOG", "MSFT", "AMZN", "FB"],
            },
        },
    )
]
func_generator = StaticFunctionItemGenerator(functions=functions)

convo = Conversation(main_agent=agent, function_generators=[func_generator])

response = convo.send_message("Please buy 100 shares of AAPL stock")
>> "Bought 100 shares of AAPL stock!"
response.content
>> "I have successfully purchased 100 shares of AAPL stock for you."
```

### Creating [Context Managers](./docs/markdown/chatmancy.conversation.md)

Context managers are used to manage context across messages. They are used to update the context based on the message history, and to provide context to the agent when generating completions. Context managers are also used to provide context to function generators, allowing for dynamic function generation.

For simple usage, you can use the built-in AgentContextManager, which will use an agent to identify context items, and will update the context based on the agent's response.

For more advanced usage, you can create a custom ContextManager. Some use cases of this include:

- Get a user from the auth service, and incldue their name, preferences and other information in the context.
- Identify another person being discussed, and insert a summary of prior interactions with them into the context.
- Identify a specific stock from context, restricted to a list of stocks that the user owns, and inclde extra information about the user's permission to buy/sell the stock.

```python
import dotenv
from chatmancy.agent import GPTAgent
from chatmancy.conversation import Conversation, AgentContextManager

dotenv.load_dotenv()


agent = GPTAgent(
    name="Literary Analyst",
    desc="A literary analyst that can discuss books and authors.",
    model="gpt-4",
    system_prompt=(
        "You are a literary analyst discussing books and authors. Answer succintly"
        " and in a literary manner."
    ),
)

book_cm = AgentContextManager(
    name="BookContextManager",
    context_item={
        "name": "book_name",
        "description": "The name of the book being discussed.",
    },
)
genre_cm = AgentContextManager(
    name="GenreContextManager",
    context_item={
        "name": "genre",
        "description": "The genre of the book or topic being discussed.",
    },
)

convo = Conversation(
    main_agent=agent,
    context_managers=[book_cm, genre_cm],
)

response = convo.send_message("Hi, lets talk about some Sci-Fi books.")
convo.context
>> {"genre": "Sci-Fi"}

response = convo.send_message("I just read Left Hand of Darkness, that was a good one.")
convo.context
>> {"genre": "Sci-Fi", "book_name": "Left Hand of Darkness"}
```
