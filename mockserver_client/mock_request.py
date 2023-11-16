import json
from typing import Dict, Any, Optional, List, Union, cast
from urllib.parse import parse_qs

from mockserver_client.mock_request_logger import MockRequestLogger


class MockRequest:
    def __init__(
        self, request: Dict[str, Any], index: int, file_path: Optional[str]
    ) -> None:
        """
        Class for mock requests

        :param request:
        """
        assert index is not None
        self.index: int = index
        assert request is not None
        assert isinstance(request, dict)
        self.request: Dict[str, Any] = request

        self.file_path: Optional[str] = file_path

        self.method: Optional[str] = self.request.get("method")
        self.path: Optional[str] = self.request.get("path")
        self.querystring_params: Dict[str, Any] | List[
            Dict[str, Any]
        ] | None = self.request.get("queryStringParameters")
        assert (
            not self.querystring_params
            or isinstance(self.querystring_params, dict)
            or isinstance(self.querystring_params, list)
        ), type(self.querystring_params)

        self.headers: Optional[Dict[str, Any]] = self.request.get("headers")

        raw_body: str | bytes | Dict[str, Any] | List[Dict[str, Any]] = cast(
            str | bytes | Dict[str, Any] | List[Dict[str, Any]],
            self.request.get("body"),
        )

        self.body_list: Optional[List[Dict[str, Any]]] = MockRequest.parse_body(
            body=raw_body, headers=self.headers
        )

        assert self.body_list is None or isinstance(
            self.body_list, list
        ), f"{type(self.body_list)}: {json.dumps(self.body_list)}"

        raw_json_content: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = (
            self.body_list[0].get("json")
            if self.body_list is not None
            and len(self.body_list) > 0
            and "json" in self.body_list[0]
            else self.body_list
            if self.body_list is not None and len(self.body_list) > 0
            else None
        )

        self.json_list: Optional[List[Dict[str, Any]]] = (
            MockRequest.parse_body(body=raw_json_content, headers=self.headers)
            if raw_json_content
            else None
        )

        assert self.json_list is None or isinstance(
            self.json_list, list
        ), f"{type(self.json_list)}: {json.dumps(self.json_list)}"

    @staticmethod
    def parse_body(
        *,
        body: Union[str, bytes, Dict[str, Any], List[Dict[str, Any]]],
        headers: Optional[Dict[str, Any]],
    ) -> Optional[List[Dict[str, Any]]]:
        # body can be either:
        # 0. None
        # 1. bytes (UTF-8 encoded)
        # 2. str (form encoded)
        # 3. str (json)
        # 3. dict
        # 4. list of string
        # 5. list of dict

        if body is None:
            return None

        if isinstance(body, bytes):
            return MockRequest.parse_body(body=body.decode("utf-8"), headers=headers)

        if isinstance(body, str):
            return MockRequest.parse_body(body=json.loads(body), headers=headers)

        if isinstance(body, dict):
            if MockRequest.is_request_content_type_form_urlencoded(body, headers):
                return [MockRequest.convert_query_parameters_to_dict(body["string"])]
            else:
                return [body]

        if isinstance(body, list):
            my_list: List[Optional[List[Dict[str, Any]]]] = [
                MockRequest.parse_body(body=c, headers=headers)
                for c in body
                if c is not None
            ]
            return [
                item
                for sublist in my_list
                if sublist is not None
                for item in sublist
                if item is not None
            ]

        assert False, f"body is in unexpected type: {type(body)}"

    @staticmethod
    def is_request_content_type_form_urlencoded(
        body: Dict[str, Any],
        headers: Optional[Union[List[Dict[str, Any]], Dict[str, Any]]],
    ) -> bool:
        """
        check the body and headers to see if this is a form urlencoded request, it is
        the body contains "string" and the headers has Content-Type of "application/x-www-form-urlencoded"
        """
        if body and "string" in body and headers:
            # sometimes headers is a list[dict] and sometimes a dict
            headers_dict = headers[0] if isinstance(headers, list) else headers
            # sometimes headers_dict will be {"name": "Content-Type", "values": ["application/x-www-form-urlencoded"]}
            # and sometimes {"Content-Type": ["application/x-www-form-urlencoded"]}
            # fmt: off
            if "application/x-www-form-urlencoded" in headers_dict.get("Content-Type", []):
                return True
            if (headers_dict.get("name") == "Content-Type" 
                    and "application/x-www-form-urlencoded" in headers_dict.get("values", [])):
                return True
            # fmt: on
        return False

    def __str__(self) -> str:
        return f"({self.index})" f" {self.path}{MockRequestLogger.convert_query_parameters_to_str(self.querystring_params)}" + (
            f": {self.json_list}" if self.json_list else ""
        ) + (
            f" from ({self.file_path})" if self.file_path else ""
        )

    @staticmethod
    def convert_query_parameters_to_dict(query: str) -> Dict[str, str]:
        params: Dict[str, List[str]] = parse_qs(query)
        return {k: v[0] for k, v in params.items()}

    def matches_without_body(self, other: "MockRequest") -> bool:
        return (
            self.method == other.method
            and self.path == other.path
            and self.querystring_params == other.querystring_params
        )
