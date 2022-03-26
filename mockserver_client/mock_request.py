import json
from typing import Dict, Any, Optional, List, Union, cast
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

        self.json_content: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = (
            json.loads(self.body_list[0].get("json"))  # type: ignore
            if self.body_list and isinstance(self.body_list[0].get("json"), str)
            else self.body_list[0].get("json")
            if self.body_list
            else None
        )
        assert (
            self.json_content is None
            or isinstance(self.json_content, dict)
            or isinstance(self.json_content, list)
        ), f"{type(self.json_content)}: {json.dumps(self.json_content)}"
        # convert strings to Dict[str, Any]
        if self.json_content is not None and isinstance(self.json_content, list):
            self.json_content = [
                (j if isinstance(j, dict) else json.loads(j)) for j in self.json_content
            ]

        if isinstance(self.json_content, list):
            for json_item in self.json_content:
                assert isinstance(
                    json_item, dict
                ), f"{type(json_item)}: {json.dumps(json_item)}"

        self.json_list: Optional[List[Dict[str, Any]]] = (
            self.json_content
            if isinstance(self.json_content, list)
            else [self.json_content]
            if self.json_content
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
            return body

        assert False, f"body is in unexpected type: {type(body)}"

    def __str__(self) -> str:
        return (
            f"url: {self.path} \nquery params: {self.querystring_params} \n"
            f"json: {self.json_content}"
        )

    @staticmethod
    def convert_query_parameters_to_dict(query: str) -> Dict[str, str]:
        params: Dict[str, List[str]] = parse_qs(query)
        return {k: v[0] for k, v in params.items()}
