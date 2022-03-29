import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from .mock_server_exception import MockServerException


class MockServerJsonContentMismatchException(MockServerException):
    """
    Exception when a request was made and an expectation with the same url was found
        but the content of the request did not match the content of the expectation
    """

    def __init__(
        self,
        actual_json: Optional[List[Dict[str, Any]]],
        expected_json: Optional[List[Dict[str, Any]]],
        differences: List[str],
        expected_file_path: Path,
    ) -> None:
        """
        Exception when a request was made and an expectation with the same url was found
            but the content of the request did not match the content of the expectation

        :param actual_json: json of actual request
        :param expected_json: json of expected request
        :param differences: differences
        :param expected_file_path:
        """
        self.actual_json: Optional[List[Dict[str, Any]]] = actual_json
        assert isinstance(actual_json, list), type(actual_json)
        self.expected_json: Optional[List[Dict[str, Any]]] = expected_json
        assert isinstance(expected_json, list), type(expected_json)
        self.differences: List[str] = differences
        assert isinstance(differences, list), type(differences)
        self.expected_file_path = expected_file_path
        assert isinstance(expected_file_path, Path), type(expected_file_path)
        error_message: str = f"Expected vs Actual: {differences} [{expected_file_path}]"
        if expected_json is None and actual_json is not None:
            error_message = f"Expected was None but Actual is {json.dumps(actual_json)}"
        elif expected_json is not None and actual_json is None:
            error_message = (
                f"Expected was {json.dumps(expected_json)} but Actual is None"
            )
        elif (
            expected_json is not None
            and actual_json is not None
            and len(self.actual_json) != len(self.expected_json)  # type: ignore
        ):
            error_message = f"Expected has {len(expected_json)} rows while actual has {len(actual_json)} rows"
        super().__init__(error_message)
