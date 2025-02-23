import json
from pathlib import Path
from typing import Dict, Any

import pytest
import requests
from deepdiff.diff import DeepDiff
from requests import put

from mockserver_client.mockserver_client import (
    MockServerFriendlyClient,
    mock_request,
    mock_response,
    times,
)
from mockserver_client.mockserver_verify_exception import MockServerVerifyException


@pytest.fixture(scope="function")
def check_active_expectations(request: pytest.FixtureRequest) -> None:
    mock_server_url = "http://mock-server:1080"

    def finalizer() -> None:
        active_expectations_response = put(
            f"{mock_server_url}/retrieve?type=active_expectations"
        )
        assert (
            active_expectations_response.status_code == 200
        ), "Failed to retrieve active expectations"
        assert (
            active_expectations_response.json() == []
        ), "There are active expectations that were not cleared"

    request.addfinalizer(finalizer)


def test_mock_server_ignore_timestamp_field(
    check_active_expectations: pytest.FixtureRequest,
) -> None:
    requests_dir: Path = Path(__file__).parent.joinpath("./requests")
    test_name = "test_mock_server"

    mock_server_url = "http://mock-server:1080"
    mock_client: MockServerFriendlyClient = MockServerFriendlyClient(
        base_url=mock_server_url, ignore_timestamp_field=True
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
                {
                    "id": "data-retrieval-start",
                    "eventNumber": "1",
                    "timestamp": "2023-11-28T00:20:56.347865+00:00",
                },
                {
                    "id": "data-retrieval-end",
                    "eventNumber": "2",
                    "timestamp": "2023-11-28T00:20:56.347865+00:00",
                },
            ],
        },
    )

    try:
        mock_client.verify_expectations(test_name=test_name)
    except MockServerVerifyException as e:
        print(str(e))
        raise e


def test_mock_server_ignore_timestamp_field_is_missing() -> None:
    """
    test that when the timestamp field is missing on a notificationEvent we only get a dictionary_item_removed difference
    for the missing timestamp field

    """
    test_name = "test_mock_server"

    mock_server_url = "http://mock-server:1080"
    mock_client: MockServerFriendlyClient = MockServerFriendlyClient(
        base_url=mock_server_url, ignore_timestamp_field=True
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
                            "timestamp": "2023-11-29T00:20:56.347865+00:00",
                        },
                        {
                            "eventNumber": "2",
                            "timestamp": "2023-11-30T00:20:56.347865+00:00",
                        },
                        {
                            "eventNumber": "3",
                            "timestamp": "2023-11-28T00:20:56.347865+00:00",
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
        file_path="foo",
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
                {"eventNumber": "2"},
                {"eventNumber": "3", "timestamp": "2023-11-28T00:21:00.347865+00:00"},
            ],
        },
    )
    with pytest.raises(MockServerVerifyException) as excinfo:
        try:
            mock_client.verify_expectations(test_name=test_name)
        except MockServerVerifyException as e:
            print(str(e))
            raise e

    assert excinfo.value.exceptions[0].differences == [  # type: ignore
        "dictionary_item_removed: root[0]['notificationEvent'][1]['timestamp']"
    ]


def test_mock_server_ignore_timestamp_element_is_missing() -> None:
    """
    test that when an entire notificationEvent element is missing we only get a difference of iterable_item_removed for the
    missing notificationEvent
    """
    test_name = "test_json_unit_delta_false_positive"

    mock_server_url = "http://mock-server:1080"
    mock_client: MockServerFriendlyClient = MockServerFriendlyClient(
        base_url=mock_server_url, ignore_timestamp_field=True
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
        file_path="foo",
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
            ],
        },
    )
    with pytest.raises(MockServerVerifyException) as excinfo:
        try:
            mock_client.verify_expectations(test_name=test_name)
        except MockServerVerifyException as e:
            print(str(e))
            raise e

    assert excinfo.value.exceptions[0].differences == [  # type: ignore
        "iterable_item_removed: root[0]['notificationEvent'][1]"
    ]


def test_mock_server_ignore_timestamp_other_value_changed() -> None:
    """
    test that we only get a value_changed error for a difference that is not a timestamp field
    """

    test_name = "test_mock_server_ignore_timestamp_other_value_changed"

    mock_server_url = "http://mock-server:1080"
    mock_client: MockServerFriendlyClient = MockServerFriendlyClient(
        base_url=mock_server_url, ignore_timestamp_field=True
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
                    "extension": [
                        {
                            "id": "data-connection-status",
                            "url": "https://www.icanbwell.com/codes/data-connection-status",
                            "valueString": "RETRIEVED",
                        }
                    ],
                    "type": "query-status",
                    "notificationEvent": [
                        {
                            "id": "data-retrieval-end",
                            "eventNumber": "2",
                            "timestamp": "2023-01-28T00:20:56.347865+00:00",
                        }
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
        file_path="foo",
    )

    http = requests.Session()
    http.post(
        mock_server_url + "/" + test_name,
        json={
            "client_id": "unitypoint_bwell",
            "client_secret": "fake_client_secret",
            "grant_type": "client",
            "extension": [
                {
                    "id": "data-connection-status",
                    "url": "https://www.icanbwell.com/codes/data-connection-status",
                    "valueString": "RETRIEVED",
                }
            ],
            "type": "query-status",
            "notificationEvent": [
                {
                    "id": "data-retrieval-end",
                    "eventNumber": "2",
                    "timestamp": "2023-11-28T00:20:56.347865+00:00",
                }
            ],
        },
    )
    with pytest.raises(MockServerVerifyException) as excinfo:
        try:
            mock_client.verify_expectations(test_name=test_name)
        except MockServerVerifyException as e:
            print(str(e))
            raise e

    assert excinfo.value.exceptions[0].differences == [  # type: ignore
        "values_changed: root[0]['grant_type']={'new_value': 'client', 'old_value': 'client_credentials'}"
    ]


def test_mock_server_ignore_timestamp_other_value_changed_and_field_missing() -> None:
    """
    test that we get a value_changed error for a difference that is not a timestamp field and a dictionary_item_removed
    error for a missing timestamp field
    """

    test_name = "test_mock_server_regex_not_working"

    mock_server_url = "http://mock-server:1080"
    mock_client: MockServerFriendlyClient = MockServerFriendlyClient(
        base_url=mock_server_url, ignore_timestamp_field=True
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
                    "extension": [
                        {
                            "id": "data-connection-status",
                            "url": "https://www.icanbwell.com/codes/data-connection-status",
                            "valueString": "RETRIEVED",
                        }
                    ],
                    "type": "query-status",
                    "notificationEvent": [
                        {
                            "id": "data-retrieval-end",
                            "eventNumber": "2",
                            "timestamp": "2023-01-28T00:20:56.347865+00:00",
                        }
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
        file_path="foo",
    )

    http = requests.Session()
    http.post(
        mock_server_url + "/" + test_name,
        json={
            "client_id": "unitypoint_bwell",
            "client_secret": "fake_client_secret",
            "grant_type": "client",
            "extension": [
                {
                    "id": "data-connection-status",
                    "url": "https://www.icanbwell.com/codes/data-connection-status",
                    "valueString": "RETRIEVED",
                }
            ],
            "type": "query-status",
            "notificationEvent": [{"id": "data-retrieval-end", "eventNumber": "2"}],
        },
    )
    with pytest.raises(MockServerVerifyException) as excinfo:
        try:
            mock_client.verify_expectations(test_name=test_name)
        except MockServerVerifyException as e:
            print(str(e))
            raise e

    assert excinfo.value.exceptions[0].differences == [  # type: ignore
        "values_changed: root[0]['grant_type']={'new_value': 'client', 'old_value': 'client_credentials'}",
        "dictionary_item_removed: root[0]['notificationEvent'][0]['timestamp']",
    ]


def test_deep_diff_with_exclude_regex_paths() -> None:
    json_1 = {
        "client_id": "unitypoint_bwell",
        "client_secret": "fake_client_secret",
        "grant_type": "client_credentials",
        "notificationEvent": [
            {
                "eventNumber": "1",
                "timestamp": "2023-01-28T00:20:56.347865+00:00",
            },
            {
                "eventNumber": "2",
                "timestamp": "2023-02-28T00:20:56.347865+00:00",
            },
            {
                "eventNumber": "3",
                "timestamp": "2023-03-28T00:20:56.347865+00:00",
            },
        ],
        "start_timestamp": "2023-03-28T00:20:56.347865+00:00",
    }
    json_2 = {
        "client_id": "unitypoint_bwell",
        "client_secret": "fake_client_secret",
        "grant_type": "client_credentials",
        "notificationEvent": [
            {"eventNumber": "1", "timestamp": "2023-11-28T00:20:56.347865+00:00"},
            {"eventNumber": "2", "timestamp": "2023-11-28T00:20:56.347865+00:00"},
            {"eventNumber": "3", "timestamp": "2023-11-28T00:21:00.347865+00:00"},
        ],
        "start_timestamp": "2023-11-28T00:20:56.347865+00:00",
    }

    diff_result = DeepDiff(
        json_1, json_2, ignore_order=True, exclude_regex_paths=[r".*\['timestamp'\]"]
    )

    assert len(diff_result.keys()) == 1
    result_items = diff_result.items()
    result_dict: Dict[str, Any] = {k: v for k, v in result_items}
    assert result_dict == {
        "values_changed": {
            "root['start_timestamp']": {
                "new_value": "2023-11-28T00:20:56.347865+00:00",
                "old_value": "2023-03-28T00:20:56.347865+00:00",
            }
        }
    }
