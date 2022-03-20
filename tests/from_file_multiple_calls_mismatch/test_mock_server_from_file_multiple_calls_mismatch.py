from glob import glob
from pathlib import Path
from typing import List, Any, Dict

import pytest
import requests
import json

from requests import Response

from mockserver_client.exceptions.mock_server_expectation_not_found_exception import (
    MockServerExpectationNotFoundException,
)
from mockserver_client.exceptions.mock_server_json_content_mismatch_exception import (
    MockServerJsonContentMismatchException,
)
from mockserver_client.mockserver_client import MockServerFriendlyClient
from mockserver_client.mockserver_verify_exception import MockServerVerifyException


def test_mock_server_from_file_multiple_calls_mismatch() -> None:
    expectations_dir: Path = Path(__file__).parent.joinpath("./expectations")
    requests_dir: Path = Path(__file__).parent.joinpath("./requests")

    test_name = "test_mock_server"

    mock_server_url = "http://mock-server:1080"
    mock_client: MockServerFriendlyClient = MockServerFriendlyClient(
        base_url=mock_server_url
    )

    mock_client.clear(f"/{test_name}/*")
    mock_client.reset()

    mock_client.expect_files_as_json_requests(
        expectations_dir, path=f"/{test_name}/foo/1/merge", json_response_body={}
    )
    mock_client.expect_default()

    http = requests.Session()

    file_path: str
    files: List[str] = sorted(
        glob(str(requests_dir.joinpath("**/*.json")), recursive=True)
    )
    for file_path in files:
        with open(file_path, "r") as file:
            content: Dict[str, Any] = json.loads(file.read())
            response: Response = http.post(
                mock_server_url + "/" + test_name + "/foo/1/merge",
                json=[content],
            )
            assert response.ok

    with pytest.raises(MockServerVerifyException):
        try:
            mock_client.verify_expectations(test_name=test_name)
        except MockServerVerifyException as e:
            # there should be two expectations.
            # One for the content not matching and one for the expectation not triggered
            assert len(e.exceptions) == 2
            json_content_mismatch_exceptions: List[
                MockServerJsonContentMismatchException
            ] = [
                e1
                for e1 in e.exceptions
                if isinstance(e1, MockServerJsonContentMismatchException)
            ]
            assert len(json_content_mismatch_exceptions) == 1
            expectation_not_found_exceptions: List[
                MockServerExpectationNotFoundException
            ] = [
                e1
                for e1 in e.exceptions
                if isinstance(e1, MockServerExpectationNotFoundException)
            ]
            assert len(expectation_not_found_exceptions) == 1
            print(str(e))
            raise e
