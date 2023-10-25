import json
from typing import Dict, Any, List, Optional


class MockResponse:
    def __init__(
        self, *, response: Dict[str, Any], index: int, file_path: Optional[str]
    ) -> None:
        assert index is not None
        assert response is not None
        assert isinstance(response, dict)
        raw_body = response.get("body")
        if isinstance(raw_body, dict):
            raw_body = json.dumps(raw_body)
        self.raw_body: Optional[str] = raw_body
        self.json_body: Dict[str, Any] | List[Dict[str, Any]] | None
        if not self.raw_body:
            self.json_body = None
        try:
            self.json_body = json.loads(self.raw_body) if self.raw_body else None
        except json.decoder.JSONDecodeError:
            self.json_body = None

        self.status_code: int | None = response.get("statusCode")
        self.index: int = index
        self.file_path: Optional[str] = file_path
