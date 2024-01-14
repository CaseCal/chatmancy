from typing import List


from ...function import (
    FunctionItem,
    FunctionItemGenerator,
)

from ...agent.base import Agent, TokenSettings
from ...agent.history import HistoryGenerator, HistoryManager
from ...agent.model import ModelHandler


class GPTAgent(Agent):
    """Agent class for generating chat responses using GPT-3."""

    def __init__(
        self,
        name: str,
        desc: str,
        model: str,
        system_prompt: str = "You are a helpful chat agent.",
        history: (List[str] | HistoryGenerator) = None,
        functions: (List[FunctionItem] | FunctionItemGenerator) = None,
        token_settings: (TokenSettings | dict) = None,
    ) -> None:
        """Create a new Agent instance.

        Args:
            name: The name of the agent.
            desc: A description of the agent.
        """
        super().__init__(
            name=name,
            desc=desc,
            model=model,
            system_prompt=system_prompt,
            history=history,
            functions=functions,
            token_settings=token_settings,
        )

    def initialize_model_handler(self, model: str, **kwargs):
        return ModelHandler(model=model)

    def initialize_history_manager(
        self, history: (List[str] | HistoryGenerator), system_prompt: str, **kwargs
    ):
        return HistoryManager(
            system_message=system_prompt,
            generator=history,
            max_prefix_tokens=self.token_settings.max_prefix_tokens,
        )
