import json
from typing import Dict, Any, Optional, List, Union
from urllib.parse import parse_qs


class MockRequest:
    def __init__(self, request: Dict[str, Any]) -> None:
        self.request: Dict[str, Any] = request
        self.method: Optional[str] = self.request.get("method")
        self.path: Optional[str] = self.request.get("path")
        self.querystring_params: Optional[Dict[str, Any]] = self.request.get(
            "queryStringParameters"
        )
        self.headers: Optional[Dict[str, Any]] = self.request.get("headers")

        raw_body = self.request.get("body")
        self.body_content: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = (
            raw_body.decode("utf-8")  # type: ignore
            if isinstance(raw_body, bytes)
            else json.loads(raw_body)
            if isinstance(raw_body, str)
            else MockRequest.convert_query_parameters_to_dict(raw_body["string"])
            if raw_body
            and "string" in raw_body
            and self.headers
            and self.headers.get("Content-Type")
            == ["application/x-www-form-urlencoded"]
            else raw_body
        )
        self.body_list: Optional[List[Dict[str, Any]]] = (
            self.body_content
            if isinstance(self.body_content, list)
            else [self.body_content]
            if self.body_content
            else None
        )

        self.json_content: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = (
            self.body_list[0].get("json") if self.body_list else None
        )
        self.json_list: Optional[List[Dict[str, Any]]] = (
            self.json_content
            if isinstance(self.json_content, list)
            else [self.json_content]
            if self.json_content
            else None
        )

    def __str__(self) -> str:
        return (
            f"url: {self.path} \nquery params: {self.querystring_params} \n"
            f"json: {self.json_content}"
        )

    @staticmethod
    def convert_query_parameters_to_dict(query: str) -> Dict[str, str]:
        params: Dict[str, List[str]] = parse_qs(query)
        return {k: v[0] for k, v in params.items()}
