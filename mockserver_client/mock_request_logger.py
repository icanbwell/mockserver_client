from typing import Dict, Any, Optional, List


class MockRequestLogger:
    @staticmethod
    def log(
        *,
        file_path: Optional[str],
        base_url: str,
        request: Dict[str, Any],
        response: Dict[str, Any] | None = None,
    ) -> None:
        """
        Prints the mock request

        :param base_url: base url
        :param file_path: file name
        :param request: mock request
        :param response: mock response
        """
        method: str = request.get("method", "GET")
        path: Optional[str] = request.get("path")
        query_string_parameters: Optional[Dict[str, Any]] = request.get(
            "queryStringParameters"
        )
        body: Optional[Dict[str, Any]] = request.get("body")
        response_body: Optional[Dict[str, Any]] = (
            response.get("body") if response else None
        )

        print(
            f"Mocking: {method} {base_url}{path}"
            + (
                f"?{MockRequestLogger.convert_query_parameters_to_str(query_string_parameters)}"
                if query_string_parameters
                else ""
            )
            + (f", from: ({file_path})" if file_path else "")
            + (f", body: {body}" if body else "")
            + (f", response: {response_body}" if response_body else "")
        )

    @staticmethod
    def convert_query_parameters_to_str(
        query_parameters: Dict[str, Any] | List[Dict[str, Any]] | None
    ) -> str:
        if query_parameters is None:
            return ""
        if isinstance(query_parameters, dict):
            return "?" + "&".join(
                [
                    f"{k}={MockRequestLogger.get_value_as_str(v)}"
                    for k, v in query_parameters.items()
                ]
            )
        assert isinstance(query_parameters, list)
        return "?" + "&".join(
            [
                f"{v.get('name')}={MockRequestLogger.get_value_as_str(v.get('values'))}"
                for v in query_parameters
            ]
        )

    @staticmethod
    def get_value_as_str(values: List[Any] | None) -> str:
        if values is not None:
            assert isinstance(values, list)
            return ",".join([str(v) for v in values])
        return ""
