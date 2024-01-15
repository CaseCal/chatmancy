from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Optional, List

from pydantic import BaseModel


from ..message import Message, AgentMessage
from .function_item import FunctionItem


class FunctionResponseMessage(Message):
    """
    Represents a response message from a function.

    Attributes:
        func_name (str): The name of the function.
        content (str): The content of the message.
        token_count (int): The number of tokens in the message.
        sender (str): The sender of the message. Defaults to 'function'
    """

    func_name: str
    func_id: str

    def __init__(self, func_name: str, func_id: str, **kwargs):
        super().__init__(
            sender="function", func_name=func_name, func_id=func_id, **kwargs
        )


class _FunctionRequest(BaseModel):
    name: str
    args: Dict
    func_item: Optional[FunctionItem] = None
    id: str


class FunctionRequestMessage(AgentMessage):
    """
    A class that represents a message.
    """

    requests: List[_FunctionRequest]

    def __init__(self, requests: List[_FunctionRequest], **kwargs):
        requests = self.create_function_requests(requests)

        super().__init__(
            requests=requests,
            content=f"Request to run functions {[r.name for r in requests]}",
            **kwargs,
        )

    def create_function_requests(cls, v):
        """
        Cast dicts to function requests
        """
        return [
            _FunctionRequest(**f) if not isinstance(f, _FunctionRequest) else f
            for f in v
        ]

    @property
    def approvals_required(self):
        return [r for r in self.requests if not r.func_item.auto_call]

    @staticmethod
    def _function_to_response(f: _FunctionRequest) -> FunctionResponseMessage:
        try:
            payload = f.func_item.call_method(**f.args)
            response = str(payload)
        except Exception as e:
            response = f"Error running function {f.name}: {e}"

        return FunctionResponseMessage(
            func_name=f.name,
            content=response,
            token_count=0,
            func_id=f.id,
        )

    @staticmethod
    def _function_to_denial(f: _FunctionRequest) -> FunctionResponseMessage:
        return FunctionResponseMessage(
            func_name=f.name,
            content=f"Function {f.name} denied.",
            token_count=0,
            func_id=f.id,
        )

    def create_responses(
        self, approved_ids: List[str] = None
    ) -> List[FunctionResponseMessage]:
        if not self.requests:
            return []
        if approved_ids is None:
            approved_ids = []

        # First filter out approved
        denied = []
        approved = []
        for f in self.requests:
            if f.func_item.auto_call or (f.id in approved_ids):
                approved.append(f)
            else:
                denied.append(f)
        denied_responses = [self._function_to_denial(f) for f in denied]
        with ThreadPoolExecutor() as pool:
            approved_responses = list(
                pool.map(lambda f: self._function_to_response(f), approved)
            )

        return denied_responses + approved_responses
