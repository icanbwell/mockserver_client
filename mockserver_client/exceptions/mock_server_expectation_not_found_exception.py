import json
from typing import Optional, Dict, Any, List

from .mock_server_exception import MockServerException


class MockServerExpectationNotFoundException(MockServerException):
    def __init__(
        self,
        url: Optional[str],
        json_list: Optional[List[Dict[str, Any]]],
        querystring_params: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.url: Optional[str] = url
        self.json_list: Optional[List[Dict[str, Any]]] = json_list
        self.querystring_params: Optional[Dict[str, Any]] = querystring_params
        super().__init__(
            f"Expectation not met: {url} {querystring_params} {json.dumps(json_list)}"
        )
