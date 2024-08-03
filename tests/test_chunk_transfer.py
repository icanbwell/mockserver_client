import http.client


def test_chunk_transfer() -> None:
    print("")
    import requests

    mock_server_url = "http://mock-server:1080"
    url = f"{mock_server_url}/mockserver/expectation"
    headers = {"Content-Type": "application/json"}
    data = {
        "httpRequest": {
            "method": "GET",
            "path": "/test_fhir_client_patient_list_async/Patient",
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
    conn = http.client.HTTPConnection("mock-server", 1080)
    conn.request(
        "GET",
        "/test_fhir_client_patient_list_async/Patient",
        headers={"Accept": "application/fhir+ndjson"},
    )

    response2 = conn.getresponse()
    print("Response status:", response2.status)
    print("Response reason:", response2.reason)

    # Read the response in chunks
    # Read the response headers to check for Transfer-Encoding: chunked
    if response2.getheader("Transfer-Encoding") == "chunked":
        print("\nResponse is chunked:\n")
        i = 0
        while True:
            i += 1
            chunk_size = response2.read(2)  # Read the chunk size
            if not chunk_size:
                break
            chunk_size1 = int(chunk_size, 16)  # Convert hex to integer
            print(f"[{i}]: Chunk size: {chunk_size1}")
            if chunk_size1 == 0:
                break
            chunk = response2.read(chunk_size1)  # Read the chunk
            print(f"[{i}]: {chunk.decode('utf-8')}", end="")
            response2.read(2)  # Read the \r\n that follows the chunk
    else:
        print("Response is not chunked.")
        data2 = response2.read()
        print(data2.decode("utf-8"))

    print("")
    conn.close()
