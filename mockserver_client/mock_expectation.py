from typing import Any, Dict

from mockserver_client._timing import _Timing
from mockserver_client.mock_request import MockRequest


class MockExpectation:
    def __init__(
        self, request: Dict[str, Any], response: Dict[str, Any], timing: _Timing
    ) -> None:
        """
        Class for Expectation

        :param request: request
        :param response: response
        :param timing: timing
        """
        self.request: MockRequest = MockRequest(request)
        self.response: Dict[str, Any] = response
        self.timing: _Timing = timing

    def __str__(self) -> str:
        return str(self.request)
