import dataclasses
from typing import List

from mockserver_client.exceptions.mock_server_exception import MockServerException
from mockserver_client.mock_request import MockRequest


@dataclasses.dataclass
class MatchRequestResult:
    exceptions: List[MockServerException]
    found_expectations: List[MockRequest]
