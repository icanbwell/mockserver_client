from pathlib import Path

from mockserver_client.mockserver_client import MockServerFriendlyClient


def test_mock_server() -> None:
    requests_dir: Path = Path(__file__).parent.joinpath("./request_json_calls")
    mock_server_url = "http://mock-server:1080"
    mock_client: MockServerFriendlyClient = MockServerFriendlyClient(
        base_url=mock_server_url
    )

    mock_client.reset()
    mock_client.expect_files_as_requests(requests_dir, url_prefix=None)

    mock_client.verify_expectations(test_name="test_framework_validation_transformer")
