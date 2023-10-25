from typing import Any, Dict, Optional

from mockserver_client._timing import _Timing
from mockserver_client.mock_request import MockRequest


class MockExpectation:
    def __init__(
        self,
        request: Dict[str, Any],
        response: Dict[str, Any],
        timing: _Timing,
        index: int,
        file_path: Optional[str],
    ) -> None:
        """
        Class for Expectation

        :param request: request
        :param response: response
        :param timing: timing
        """
        self.request: MockRequest = MockRequest(
            request=request, index=index, file_path=file_path
        )
        self.response: Dict[str, Any] = response
        self.timing: _Timing = timing

    def __str__(self) -> str:
        return str(self.request)
