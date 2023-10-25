from typing import Dict, Any

from mockserver_client.mock_request import MockRequest
from mockserver_client.mock_response import MockResponse


class MockRequestResponse:
    def __init__(
        self,
        *,
        request: Dict[str, Any] | None,
        response: Dict[str, Any] | None,
        index: int,
        file_path: str | None = None,
    ):
        self.raw_request: Dict[str, Any] | None = request
        self.request: MockRequest | None = (
            MockRequest(request=request, index=index, file_path=file_path)
            if request
            else None
        )
        self.raw_response: Dict[str, Any] | None = response
        self.response: MockResponse | None = (
            MockResponse(response=response, index=index, file_path=file_path)
            if response
            else None
        )
        self.file_path: str | None = file_path
