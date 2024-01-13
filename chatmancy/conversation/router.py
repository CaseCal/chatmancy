from typing import Dict

from ..agent import Agent
from ..message import Message


class ChatRouter:
    def get_agent(self, context: Dict) -> Agent | Message:
        raise NotImplementedError
