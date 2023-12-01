import json
from pathlib import Path

import pytest
import requests

from mockserver_client.mockserver_client import (
    MockServerFriendlyClient,
    mock_request,
    mock_response,
    times,
)
from mockserver_client.mockserver_verify_exception import MockServerVerifyException


def test_mock_server_json_unit_ignore_element() -> None:
    requests_dir: Path = Path(__file__).parent.joinpath("./requests")
    test_name = "test_mock_server"

    mock_server_url = "http://mock-server:1080"
    mock_client: MockServerFriendlyClient = MockServerFriendlyClient(
        base_url=mock_server_url
    )

    mock_client.clear(f"/{test_name}/*.*")
    mock_client.reset()
    mock_client.expect_files_as_requests(
        requests_dir,
        url_prefix=test_name,
    )

    http = requests.Session()
    http.post(
        mock_server_url + "/" + test_name,
        json={
            "client_id": "unitypoint_bwell",
            "client_secret": "fake_client_secret",
            "grant_type": "client_credentials",
            "notificationEvent": [
                {"eventNumber": "1", "timestamp": "2023-11-28T00:20:56.347865+00:00"},
                {"eventNumber": "2", "timestamp": "2023-11-28T00:20:56.347865+00:00"},
            ],
        },
    )

    try:
        mock_client.verify_expectations(test_name=test_name)
    except MockServerVerifyException as e:
        print(str(e))
        raise e


def test_mock_server_json_unit_ignore_element_missing() -> None:
    test_name = "test_mock_server"

    mock_server_url = "http://mock-server:1080"
    mock_client: MockServerFriendlyClient = MockServerFriendlyClient(
        base_url=mock_server_url
    )

    mock_client.clear(f"/{test_name}/*.*")
    mock_client.reset()
    mock_client.expect(
        request=mock_request(
            path="/" + test_name,
            method="POST",
            body={
                "json": {
                    "client_id": "unitypoint_bwell",
                    "client_secret": "fake_client_secret",
                    "grant_type": "client_credentials",
                    "notificationEvent": [
                        {
                            "eventNumber": "1",
                            "timestamp": "${json-unit.ignore-element}",
                        },
                        {
                            "eventNumber": "2",
                            "timestamp": "${json-unit.ignore-element}",
                        },
                        {
                            "eventNumber": "3",
                            "timestamp": "${json-unit.ignore-element}",
                        },
                    ],
                }
            },
        ),
        response=mock_response(
            body=json.dumps(
                {
                    "token_type": "bearer",
                    "access_token": "fake access_token",
                    "expires_in": 54000,
                }
            )
        ),
        timing=times(1),
        file_path=None,
    )

    http = requests.Session()
    http.post(
        mock_server_url + "/" + test_name,
        json={
            "client_id": "unitypoint_bwell",
            "client_secret": "fake_client_secret",
            "grant_type": "client_credentials",
            "notificationEvent": [
                {"eventNumber": "1", "timestamp": "2023-11-28T00:20:56.347865+00:00"},
                {
                    "eventNumber": "2",
                },
                {"eventNumber": "3", "timestamp": "2023-11-28T00:21:00.347865+00:00"},
            ],
        },
    )
    with pytest.raises(MockServerVerifyException):
        try:
            mock_client.verify_expectations(test_name=test_name)
        except MockServerVerifyException as e:
            print(str(e))
            raise e
