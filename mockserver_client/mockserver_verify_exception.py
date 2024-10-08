import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from .exceptions.mock_server_exception import MockServerException
from .exceptions.mock_server_json_content_mismatch_exception import (
    MockServerJsonContentMismatchException,
)
from .mock_request import MockRequest


class MockServerVerifyException(Exception):
    def __init__(
        self,
        exceptions: List[MockServerException],
        found_expectations: List[MockRequest],
        files: Optional[List[str]] = None,
    ) -> None:
        """
        Exception when mock server found the mismatch

        :param exceptions:
        :param files:
        """
        super().__init__()
        self.exceptions: List[MockServerException] = exceptions
        self.found_expectations: List[MockRequest] = found_expectations
        self.files: List[str] = files or []
        self.set_files_in_exceptions()

    def set_files_in_exceptions(self) -> None:
        # iterate through the exceptions and find the corresponding files
        exception: MockServerException
        for exception in self.exceptions:
            if isinstance(exception, MockServerJsonContentMismatchException):
                actual_list_or_obj: Optional[List[Dict[str, Any]]] = (
                    exception.actual_json
                )
                if actual_list_or_obj:
                    for actual in actual_list_or_obj:
                        if "resourceType" in actual and "id" in actual:
                            # noinspection PyPep8Naming
                            resourceType: str = actual["resourceType"]
                            id_: str = actual["id"]
                            # now iterate through the files to find the file for this
                            file_name: str
                            for file_name in self.files:
                                with open(file_name, "r") as file:
                                    json_data = json.loads(file.read())
                                    if isinstance(json_data, list):
                                        for json_data1 in json_data:
                                            if (
                                                json_data1["resourceType"]
                                                == resourceType
                                                and json_data1["id"] == id_
                                            ):
                                                exception.expected_file_path = Path(
                                                    file_name
                                                )
                                    else:
                                        if (
                                            json_data["resourceType"] == resourceType
                                            and json_data["id"] == id_
                                        ):
                                            exception.expected_file_path = Path(
                                                file_name
                                            )

    def __str__(self) -> str:
        return ",".join(
            [
                str(e.expected_file_path)
                for e in self.exceptions
                if isinstance(e, MockServerJsonContentMismatchException)
            ]
        )
