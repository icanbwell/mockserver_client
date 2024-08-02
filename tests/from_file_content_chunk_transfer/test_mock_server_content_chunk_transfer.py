from pathlib import Path

import requests

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

    http = requests.Session()
    # expectation file content_type_form_urlencoded_string_body
    # this expectation is set up in the preferred way for "Content-Type": "application/x-www-form-urlencoded"
    matched_response = http.get(
        mock_server_url + "/" + test_name, headers={"Accept": "application/fhir+ndjson"}
    )
    assert matched_response.status_code == 200
    assert (
        matched_response.content
        == b'8e\r\n{"resourceType":"Patient","id":"3456789012345670303","meta":{"profile":["http://hl7.org/fhir/us/carin/StructureDefinition/carin-bb-coverage"]}\r\n527\r\n"identifier":[{"type":{"coding":[{"system":"http://terminology.hl7.org/CodeSystem/v2-0203","code":"SN"}]},"system":"https://sources.aetna.com/coverage/identifier/membershipid/59","value":"435679010300+AE303+2021-01-01"}],"status":"active","type":{"coding":[{"system":"http://terminology.hl7.org/CodeSystem/v3-ActCode","code":"PPO","display":"preferred provider organization policy"}]},"policyHolder":{"reference":"Patient/1234567890123456703","type":"Patient"},"subscriber":{"reference":"Patient/1234567890123456703","type":"Patient"},"subscriberId":"435679010300","beneficiary":{"reference":"Patient/1234567890123456703","type":"Patient"},"relationship":{"coding":[{"system":"http://terminology.hl7.org/CodeSystem/subscriber-relationship","code":"self"}]},"period":{"start":"2021-01-01","end":"2021-12-31"},"payor":[{"reference":"Organization/6667778889990000014","type":"Organization","display":"Aetna"}],"class":[{"type":{"coding":[{"system":"http://terminology.hl7.org/CodeSystem/coverage-class","code":"plan","display":"Plan"}]},"value":"AE303","name":"Aetna Plan"}],"network":"Medicare - MA/NY/NJ - Full Reciprocity","costToBeneficiary":[{"type":{"text":"Annual Physical Exams NMC - In Network"},"valueQuantity":{"value":50,"unit":"$","system":"http://aetna.com/Medicare/CostToBeneficiary/ValueQuantity/code"}}]}"\r\n0\r\n\r\n'
    )

    try:
        mock_client.verify_expectations(test_name=test_name)
    except MockServerVerifyException as e:
        print(str(e))
        raise e
