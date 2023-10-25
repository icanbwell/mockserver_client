import json
from typing import Optional, Dict, Any, List

from .mock_server_exception import MockServerException
from ..mock_request import MockRequest


class MockServerExpectationNotFoundException(MockServerException):
    """
    Exception when a request was made but an expectation was not found for it
    """

    def __init__(
        self,
        *,
        method: Optional[str],
        url: Optional[str],
        json_list: Optional[List[Dict[str, Any]]],
        querystring_params: Dict[str, Any] | List[Dict[str, Any]] | None = None,
        expectation: MockRequest,
    ) -> None:
        """
        Exception when a request was made but an expectation was not found for it


        :param url: url of expectation not found
        :param json_list: json body
        :param querystring_params: query string
        :param expectation
        """
        self.method: Optional[str] = method
        self.url: Optional[str] = url
        self.json_list: Optional[List[Dict[str, Any]]] = json_list
        self.querystring_params: Dict[str, Any] | List[
            Dict[str, Any]
        ] | None = querystring_params
        self.expectation: MockRequest = expectation
        super().__init__(
            f"Expectation not met: {method} {url} {querystring_params!r} "
            + f"{json.dumps(json_list) if json_list else '(No body)'}"
        )
