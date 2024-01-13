import logging
from typing import Dict, List, Optional

from ..message import MessageQueue, Message, UserMessage, AgentMessage
from ..agent import Agent
from ..function import (
    FunctionItemGenerator,
    FunctionItem,
    FunctionRequestMessage,
    FunctionResponseMessage,
)
from .context_manager import ContextManager
from .cache import CacheInterface
from ..logging import trace


class Conversation:
    user_message_history: MessageQueue
    _context: Dict[str, str]
    main_agent: Agent
    context_managers: List[ContextManager]

    def __init__(
        self,
        main_agent: Agent,
        opening_prompt: str = "Hello!",
        context_managers: List[ContextManager] = None,
        function_generators: List[FunctionItemGenerator] = None,
        function_cache: Optional[CacheInterface[str, List[FunctionItem]]] = None,
        history=None,
        name: str = None,
        context: Dict[str, str] = None,
    ) -> None:
        # Validate types
        self._validate(main_agent, opening_prompt, context_managers, history, context)

        # Set attributes for hot-loading
        self.user_message_history = (
            history
            if history is not None
            else MessageQueue([AgentMessage(content=opening_prompt)])
        )
        self._context = context if context is not None else {}
        self.function_cache = function_cache
        self.name = name

        # Spin up agents
        self.main_agent = main_agent
        self.opening_prompt = opening_prompt

        if context_managers is None:
            context_managers = []
        self.context_managers = context_managers
        if function_generators is None:
            function_generators = []
        self.function_generators = function_generators

        self.logger = logging.getLogger("Conversation")
        self.logger.setLevel("INFO")

    def _validate(self, main_agent, opening_prompt, context_managers, history, context):
        if not isinstance(main_agent, Agent):
            raise TypeError(
                f"main_agent must be an instance of Agent, not {type(main_agent)}"
            )
        if not isinstance(opening_prompt, str):
            raise TypeError(
                f"opening_prompt must be a string, not {type(opening_prompt)}"
            )
        if context_managers is not None:
            if not isinstance(context_managers, list):
                raise TypeError(
                    f"context_managers must be a list, not {type(context_managers)}"
                )
            for cm in context_managers:
                if not isinstance(cm, ContextManager):
                    raise TypeError(
                        f"Context manager {cm} is not an instance of ContextManager"
                    )
        if history is not None:
            if not isinstance(history, MessageQueue):
                raise TypeError(
                    f"history must be an instance of MessageQueue, not {type(history)}"
                )
        if context is not None:
            if not isinstance(context, dict):
                raise TypeError(
                    f"context must be a dict, not {type(context)}: {context}"
                )

    def _message_agent(self, agent: Agent, message: Message) -> Message:
        """
        Send message to the specified agent, and record message and response in
        user message history.
        """
        self.logger.info(f"Current context is {self.context}")

        # Create functions
        functions = self._create_functions(
            message, self.user_message_history.copy(), self.context.copy()
        )

        # Get response and update history
        agent_response: Message = agent.get_response_message(
            message,
            self.user_message_history.copy(),
            context=self.context.copy(),
            functions=functions,
        )

        # Update history
        self.user_message_history.extend([message, agent_response])

        # Check function requests
        if isinstance(agent_response, FunctionRequestMessage):
            function_response = self._handle_function_request(agent_response, functions)

            # Pass along unapproved requests
            if isinstance(function_response, FunctionRequestMessage):
                return function_response
            else:
                # Return to agent with auto-call requests
                return self._message_agent(agent, function_response)

        return agent_response

    def ask_question(self, question: str) -> Message:
        """
        Send message to main agent, and record message and response in user
        message history.
        """
        m = UserMessage(question)
        return self.send_message(m)

    @property
    def context(self):
        return {**self._context}

    @trace(name="Conversation.ask_question")
    def send_message(self, message: Message) -> Message:
        """
        Sends a message to the conversation and returns the response.

        Args:
            message (Message): The message to send.

        Returns:
            Message: The response message.
        """
        # Update context
        self._update_context([message])

        # Send message to agent
        return self._message_agent(self.main_agent, message)

    def _update_context(self, extra_messages: List[Message] = None):
        if extra_messages is None:
            extra_messages = []
        history = self.user_message_history.copy()
        history.extend(extra_messages)
        for cm in self.context_managers:
            additions = cm.get_context_updates(history, self._context)
            if additions is not None:
                self._context.update(additions)

    def _create_functions(
        self, input_message: Message, history: MessageQueue, context: Dict[str, str]
    ) -> List[FunctionItem]:
        functions = []
        for fg in self.function_generators:
            # Generate a cache key using the FunctionItemGenerator's method
            cache_key = fg.create_cache_key(input_message, history, context)

            # Check if the functions are already in the user-provided cache
            cached_functions = (
                None
                if self.function_cache is None
                else self.function_cache.get(cache_key)
            )
            if cached_functions is not None:
                self.logger.info(f"Using cached functions for {cache_key}")
                functions.extend(cached_functions)
            else:
                self.logger.info(
                    f"No cache foudn for {cache_key}, generating functions"
                )
                # If not in cache, generate the functions and store them in the cache
                generated_functions = fg.generate_functions(
                    input_message=input_message, history=history, context=context
                )
                functions.extend(generated_functions)
                if self.function_cache is not None:
                    self.function_cache.set(cache_key, generated_functions)
        return functions

    @trace(name="Conversation._handle_function_request")
    def _handle_function_request(
        self, request: FunctionRequestMessage, functions: list[FunctionItem]
    ):
        """
        Handles a function request. Finds the function in the list of
        functions and calls it.
        If function is not in list, creates message to agent saying function
        could not be found.
        If function is auto-call, calls function and returns response.
        Otherwise, returns the function request with the function item attached.
        """

        # Get function item
        try:
            fi = [f for f in functions if f.name == request.func_name][0]
        except IndexError:
            error_message = self.token_handler.create_message(
                "function",
                f"Function {request.func_name} not found in list of functions.",
            )
            return error_message

        # Handle function call if auto
        if fi.auto_call:
            function_payload = fi.call_method(**request.func_args)
            self.logger.info(
                f"Function {request.func_name} returned {function_payload}"
            )

            new_message = FunctionResponseMessage(
                func_name=request.func_name,
                content=function_payload,
                token_count=self.token_handler.count_tokens(function_payload),
            )
            return new_message

        # Add function item to message and return
        request.func_item = fi
        return request
