from pathlib import Path
from typing import List

import requests
from requests import Response

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

    # expectation file content_type_form_urlencoded_string_body
    # this expectation is set up in the preferred way for "Content-Type": "application/x-www-form-urlencoded"
    # Step 2: Make a GET request to the specified path and check if the response is chunked
    matched_response: Response = requests.get(
        mock_server_url + "/" + test_name,
        headers={"Accept": "application/fhir+ndjson"},
        stream=True,
    )

    assert matched_response.status_code == 200
    assert matched_response.headers["Transfer-Encoding"] == "chunked"

    chunk_number = 0
    chunks: List[str] = []
    chunk: bytes
    for chunk in matched_response.raw.read_chunked():
        chunk_number += 1
        print(f"{chunk_number}: {chunk!r}")
        chunks.append(chunk.decode("utf-8"))

    assert chunk_number == 15
    assert (
        chunks[0]
        == '{"resourceType":"Patient","id":"3456789012345670303","meta":{"profile":["http://hl7.org/fhir/us/cari'
    )

    # now verify the expectations were met
    try:
        mock_client.verify_expectations(test_name=test_name)
    except MockServerVerifyException as e:
        print(str(e))
        raise e
