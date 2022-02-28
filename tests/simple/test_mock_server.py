from pathlib import Path

import requests

from mockserver_client.mockserver_client import MockServerFriendlyClient


def test_mock_server() -> None:
    requests_dir: Path = Path(__file__).parent.joinpath("./request_json_calls")
    test_name = "test_mock_server"

    mock_server_url = "http://mock-server:1080"
    mock_client: MockServerFriendlyClient = MockServerFriendlyClient(
        base_url=mock_server_url
    )

    mock_client.clear(f"/{test_name}/*.*")
    mock_client.expect_files_as_requests(requests_dir, url_prefix=test_name)

    http = requests.Session()
    http.post(
        mock_server_url + "/" + test_name,
        data={
            "client_id": "unitypoint_bwell",
            "client_secret": "fake_client_secret",
            "grant_type": "client_credentials",
        },
    )
    mock_client.verify_expectations(test_name=test_name)
