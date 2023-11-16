from pathlib import Path

import requests

from mockserver_client.mock_requests_loader import load_mock_source_api_json_responses
from mockserver_client.mockserver_client import MockServerFriendlyClient
from mockserver_client.mockserver_verify_exception import MockServerVerifyException


def test_mock_server_from_file_content_type_form_urlencoded() -> None:
    requests_dir: Path = Path(__file__).parent.joinpath("./expectations")
    test_name = "test_mock_server"

    mock_server_url = "http://mock-server:1080"
    mock_client: MockServerFriendlyClient = MockServerFriendlyClient(
        base_url=mock_server_url
    )

    mock_client.clear(f"/{test_name}/*.*")
    mock_client.reset()

    load_mock_source_api_json_responses(
        folder=requests_dir,
        mock_client=mock_client,
        url_prefix=test_name,
    )

    http = requests.Session()
    # expectation file content_type_form_urlencoded_string_body
    # this expectation is set up in the preferred way for "Content-Type": "application/x-www-form-urlencoded"
    matched_response = http.post(
        mock_server_url + "/" + test_name,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={"member_id": "12345", "status": "active"},
    )
    assert matched_response.status_code == 200

    # expectation file content_type_form_urlencoded_not_matched
    # this is a fun one because mock-server will not match the request because the service_slug value is being
    # coerced to an integer by mock-server when doing the matching. this seems to only happen for requests
    # with "Content-Type": "application/x-www-form-urlencoded
    not_found_response = http.post(
        mock_server_url + "/" + test_name + "/api/v1.0/update_token_status",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "member_id": "xy18376",
            "service_slug": "2222",
            "status": "Retrieving Data",
        },
    )
    assert (
        not_found_response.status_code == 404
    ), "mock server x-www-form-urlencoded issue is resolved!"

    # expectation file content_type_form_urlencoded_matched
    # this mocked request is the same as the previous except the service_slug value is now a string due to the
    # inclusion of an alphanumeric character. this request will match the mock-server expectation
    matched_response = http.post(
        mock_server_url + "/" + test_name + "/api/v1.0/update_token_status",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "member_id": "xy18376",
            "service_slug": "2222a",
            "status": "Retrieving Data",
        },
    )

    assert matched_response.status_code == 200

    try:
        mock_client.verify_expectations(test_name=test_name)
    except MockServerVerifyException as e:
        print(str(e))
        raise e
