from typing import List

from requests import Response


def test_chunk_transfer() -> None:
    print("")
    import requests

    test_name: str = "test_chunk_transfer"

    mock_server_url = "http://mock-server:1080"
    url = f"{mock_server_url}/mockserver/expectation"
    headers = {"Content-Type": "application/json"}
    data = {
        "httpRequest": {
            "method": "GET",
            "path": f"/{test_name}",
        },
        "httpResponse": {
            "body": "1234567890",
            "headers": {"Transfer-Encoding": "chunked"},
            "connectionOptions": {"chunkSize": 2},
        },
        "id": "77cd67c4-c470-470d-99a8-b1fe85c0c083",
        "priority": 0,
        "timeToLive": {"unlimited": True},
        "times": {"remainingTimes": 1},
    }

    response = requests.put(url, headers=headers, json=data)

    if response.status_code == 201 or response.status_code == 200:
        print("Expectation created successfully.")
    else:
        print(f"Failed to create expectation: {response.status_code}")
        print(response.text)
        exit()

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

    assert chunk_number == 5
    assert chunks[0] == "12"
