from typing import Any, Dict, List, Optional

from .mock_server_exception import MockServerException


class MockServerRequestNotFoundException(MockServerException):
    """
    Exception when we found no expectation for a request
    """

    def __init__(
        self,
        method: Optional[str],
        url: Optional[str],
        json_list: Optional[List[Dict[str, Any]]],
    ) -> None:
        """
        Exception when we found no expectation for a request

        :param method: method of request
        :param url: url of request
        :param json_list: json body
        """
        self.method: Optional[str] = method
        self.url: Optional[str] = url
        self.json_dict: Optional[List[Dict[str, Any]]] = json_list
        assert (
            not json_list or isinstance(json_list, dict) or isinstance(json_list, list)
        ), type(json_list)
        super().__init__(f"Request was not expected: {url} {json_list}")
