# mockserver_client
It has docker based image: ``jamesdbloom/mockserver:mockserver-5.13.*``

As pip dependency could be found here: https://pypi.org/project/helix-mockserver-client/

In your ``requirements.txt`` or ```PipFile```  add ```helix-mockserver-client>=*.*.*```

Basic usage:

```python
import json
from mockserver_client.mockserver_client import (
    MockServerFriendlyClient,
    mock_request,
    mock_response,
    times,
)
 mock_server = MockServerFriendlyClient('http://127.0.0.1:1080')
 mock_server.expect(mock_request(
            path="/" + 'item',
            method="POST",
            body={
                "json": {
                    "client_id": "unitypoint_bwell",
                    "client_secret": "fake_client_secret",
                    "grant_type": "client_credentials",
                }
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
```
How to pull the image with Docker:
```docker pull jamesdbloom/mockserver:mockserver-5.13.2```

How to start the server locally with Docker:
```docker run -dp 1080:1080 jamesdbloom/mockserver:mockserver-5.13.2 -logLevel DEBUG -serverPort 1080```
