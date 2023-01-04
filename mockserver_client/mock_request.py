import json
from typing import Dict, Any, Optional, List, Union, cast
from urllib.parse import parse_qs


class MockRequest:
    def __init__(self, request: Dict[str, Any]) -> None:
        """
        Class for mock requests

        :param request:
        """
        self.request: Dict[str, Any] = request
        self.method: Optional[str] = self.request.get("method")
        self.path: Optional[str] = self.request.get("path")
        self.querystring_params: Optional[Dict[str, Any]] = self.request.get(
            "queryStringParameters"
        )
        self.headers: Optional[Dict[str, Any]] = self.request.get("headers")

        raw_body: Union[str, bytes, Dict[str, Any], List[Dict[str, Any]]] = cast(
            Union[str, bytes, Dict[str, Any], List[Dict[str, Any]]],
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
            if (
                body
                and "string" in body
                and headers
                and headers.get("Content-Type") == ["application/x-www-form-urlencoded"]
            ):
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

    def __str__(self) -> str:
        return (
            f"url: {self.path} \nquery params: {self.querystring_params} \n"
            f"json: {self.json_list}"
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
