import json

import pytest
import requests

from mockserver_client.mockserver_client import (
    MockServerFriendlyClient,
    mock_request,
    mock_response,
    times,
)
from mockserver_client.mockserver_verify_exception import MockServerVerifyException


def test_mock_server_inline_fail() -> None:
    test_name = "test_mock_server_inline_fail"

    mock_server_url = "http://mock-server:1080"
    mock_client: MockServerFriendlyClient = MockServerFriendlyClient(
        base_url=mock_server_url
    )

    mock_client.clear(f"/{test_name}/*.*")

    mock_client.expect(
        mock_request(
            path="/" + test_name,
            method="POST",
            body={
                "client_id": "unitypoint_bwell",
                "client_secret": "fake_client_secret",
                "grant_type": "client_credentials",
            },
        ),
        mock_response(
            body=json.dumps(
                {
                    "token_type": "bearer",
                    "access_token": "fake access_token",
                    "expires_in": 54000,
                }
            )
        ),
        timing=times(1),
    )

    http = requests.Session()
    http.post(
        mock_server_url + "/" + test_name,
        data={"client_id": "unitypoint_bwell", "client_secret": "fake_client_secret"},
    )

    with pytest.raises(MockServerVerifyException):
        mock_client.verify_expectations(test_name=test_name)
