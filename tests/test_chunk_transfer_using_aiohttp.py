from typing import List
import aiohttp


async def test_chunk_transfer_using_aiohttp() -> None:
    print("")
    test_name: str = "test_chunk_transfer_using_aiohttp"

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

    async with aiohttp.ClientSession() as session:
        async with session.put(url, headers=headers, json=data) as response:
            if response.status == 201 or response.status == 200:
                print("Expectation created successfully.")
            else:
                print(f"Failed to create expectation: {response.status}")
                print(await response.text())
                return

        # Step 2: Make a GET request to the specified path and check if the response is chunked
        async with session.get(
            mock_server_url + "/" + test_name,
            headers={"Accept": "application/fhir+ndjson"},
            chunked=True,
        ) as matched_response:
            assert matched_response.status == 200
            assert matched_response.headers["Transfer-Encoding"] == "chunked"

            chunk_number = 0
            chunks: List[str] = []
            chunk: bytes
            async for (
                chunk,
                end_of_http_chunk,
            ) in matched_response.content.iter_chunks():
                chunk_number += 1
                chunk_txt = chunk.decode("utf-8")
                print(
                    f"{chunk_number}: {chunk_txt} end_of_http_chunk={end_of_http_chunk}"
                )
                chunks.append(chunk_txt)

            assert chunk_number == 5
            assert chunks[0] == "12"
