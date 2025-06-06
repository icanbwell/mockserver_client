from pathlib import Path
from typing import List
import pytest

from mockserver_client.mock_requests_loader import (
    bulk_laod_mock_fhir_requests_from_folder,
)
from mockserver_client.mockserver_client import MockServerFriendlyClient


@pytest.fixture
def expectations_dir() -> Path:
    return Path(__file__).parent.joinpath("./expectation")


@pytest.fixture
def mock_client() -> MockServerFriendlyClient:
    return MockServerFriendlyClient(base_url="http://mock-server:1080")


def test_bulk_load_calls_register_expectation_for_each_file(
    expectations_dir: Path, mock_client: MockServerFriendlyClient
) -> None:
    files = list(expectations_dir.glob("*.json"))
    assert files, "No JSON files found in expectation folder for testing"

    read_files: List[str] = []
    try:
        read_files = bulk_laod_mock_fhir_requests_from_folder(
            folder=expectations_dir,
            mock_client=mock_client,
            method="POST",
            query_string={"smartMerge": ["false"]},
            url_prefix="/test/bulk_load_mock_fhir_requests_from_folder",
        )
    except Exception as e:
        raise AssertionError(f"An error occurred during bulk load: {e}")

    assert len(read_files) == len(files)
