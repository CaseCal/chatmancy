import logging
from typing import Dict, List

from chatmancy.function.function_message import _FunctionRequest

from ..message import MessageQueue, Message, UserMessage, AgentMessage
from ..agent import Agent
from ..function import (
    FunctionItemGenerator,
    FunctionItem,
    FunctionRequestMessage,
    FunctionResponseMessage,
)
from .context_manager import ContextManager
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

        self.logger = logging.getLogger("chatmancy.Conversation")
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
            function_response = self._handle_function_request_message(
                agent_response, functions
            )

            # Pass along unapproved requests
            if isinstance(function_response, FunctionRequestMessage):
                return function_response
            else:
                return self._send_agent_responses(agent, function_response)

        return agent_response

    def _send_agent_responses(self, agent: Agent, responses: List[Message]) -> Message:
        """
        Sends a list of messages to the agent and updates the history.
        """
        self.logger.info(f"Sending {len(responses)} response messages to agent")
        self.logger.debug(f"Messages: {responses}")
        self.user_message_history.extend(responses)
        return agent.give_function_response(self.user_message_history.copy())

    @property
    def context(self):
        return {**self._context}

    @trace(name="Conversation.ask_question")
    def send_message(self, message: (Message | str)) -> Message:
        """
        Sends a message to the conversation and returns the response.

        Args:
            message (Message): The message to send.

        Returns:
            Message: The response message.
        """
        # Validate message
        if isinstance(message, str):
            message = UserMessage(content=message)
        elif not isinstance(message, Message):
            raise TypeError(f"message must be a string or Message, not {type(message)}")

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
            # generate the functions
            generated_functions = fg.generate_functions(
                input_message=input_message, history=history, context=context
            )
            functions.extend(generated_functions)
        return functions

    def _handle_function_request_message(
        self, request_message: FunctionRequestMessage, functions: list[FunctionItem]
    ) -> FunctionRequestMessage | List[FunctionResponseMessage]:
        """
        Handles a function request. Finds the function in the list of
        functions and calls it.
        If function is not in list, creates message to agent saying function
        could not be found.
        If function is auto-call, calls function and returns response.
        Otherwise, returns the function request with the function item attached.
        """
        self.logger.info("Handling function request message")
        self.logger.debug(f"Request message: {request_message}")
        errors = []
        for request in request_message.requests:
            # Attach fi
            try:
                self._attach_function_item(request, functions)
            except ValueError as e:
                self.logger.exception(
                    f"Could not find function {request.name} in {functions}"
                )
                errors.append(
                    FunctionResponseMessage(
                        func_name=request.name,
                        func_id=request.id,
                        content=f"Error: {e}",
                    )
                )
                continue

        if errors:
            self.logger.warning("Errors found, returning errors")
            return errors

        # If no approval, call and return
        if not request_message.approvals_required:
            self.logger.info("All functions are autocall, calling them")
            return request_message.create_responses()

        # Pass on the full request if any approvals are required
        self.logger.info("Some functions require approval, passing on request")
        return request_message

    def _attach_function_item(
        self, request: _FunctionRequest, functions: List[FunctionItem]
    ) -> None:
        """
        Attaches function items to function requests.
        """
        # Get function item
        try:
            fi = [f for f in functions if f.name == request.name][0]
        except IndexError:
            raise ValueError(f"Function {request.name} not found in {functions}")
        request.func_item = fi
