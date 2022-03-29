import json
from typing import Optional, Dict, Any, List

from .mock_server_exception import MockServerException


class MockServerExpectationNotFoundException(MockServerException):
    """
    Exception when a request was made but an expectation was not found for it
    """

    def __init__(
        self,
        url: Optional[str],
        json_list: Optional[List[Dict[str, Any]]],
        querystring_params: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Exception when a request was made but an expectation was not found for it


        :param url: url of expectation not found
        :param json_list: json body
        :param querystring_params: query string
        """
        self.url: Optional[str] = url
        self.json_list: Optional[List[Dict[str, Any]]] = json_list
        self.querystring_params: Optional[Dict[str, Any]] = querystring_params
        super().__init__(
            f"Expectation not met: {url} {querystring_params} {json.dumps(json_list)}"
        )
