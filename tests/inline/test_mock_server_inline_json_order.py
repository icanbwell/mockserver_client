import json

import requests

from mockserver_client.mockserver_client import (
    MockServerFriendlyClient,
    mock_request,
    mock_response,
    times,
)
from mockserver_client.mockserver_verify_exception import MockServerVerifyException


def test_mock_server_inline_json_order() -> None:
    test_name = "test_mock_server_inline"

    mock_server_url = "http://mock-server:1080"
    mock_client: MockServerFriendlyClient = MockServerFriendlyClient(
        base_url=mock_server_url
    )

    mock_client.clear(f"/{test_name}/*.*")

    mock_client.expect(
        request=mock_request(
            path="/" + test_name,
            method="POST",
            body={
                "json": {
                    "resourceType": "Coverage",
                    "id": "aetna-sandbox-3456789012345670303",
                    "meta": {
                        "source": "http://mock-server:1080/test_patient_access_pipeline/source/4_0_0/Coverage/3456789012345670303",
                        "security": [
                            {
                                "system": "https://www.icanbwell.com/owner",
                                "code": "aetna_sandbox",
                            },
                            {
                                "system": "https://www.icanbwell.com/access",
                                "code": "aetna_sandbox",
                            },
                            {
                                "system": "https://www.icanbwell.com/vendor",
                                "code": "aetna_sandbox",
                            },
                            {
                                "system": "https://www.icanbwell.com/connectionType",
                                "code": "proa",
                            },
                        ],
                    },
                    "identifier": [
                        {
                            "type": {
                                "coding": [
                                    {
                                        "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
                                        "code": "SN",
                                    }
                                ]
                            },
                            "system": "https://sources.aetna.com/coverage/identifier/membershipid/59",
                            "value": "435679010300+AE303+2021-01-01",
                        }
                    ],
                    "status": "active",
                    "type": {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                                "code": "PPO",
                                "display": "preferred provider organization policy",
                            }
                        ]
                    },
                    "policyHolder": {
                        "reference": "Patient/aetna-sandbox-1234567890123456703",
                        "type": "Patient",
                    },
                    "subscriber": {
                        "reference": "Patient/aetna-sandbox-1234567890123456703",
                        "type": "Patient",
                    },
                    "subscriberId": "435679010300",
                    "beneficiary": {
                        "reference": "Patient/aetna-sandbox-1234567890123456703",
                        "type": "Patient",
                    },
                    "relationship": {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/CodeSystem/subscriber-relationship",
                                "code": "self",
                            }
                        ]
                    },
                    "period": {"start": "2021-01-01", "end": "2021-12-31"},
                    "payor": [
                        {
                            "reference": "Organization/aetna-sandbox-6667778889990000014",
                            "type": "Organization",
                            "display": "Aetna",
                        }
                    ],
                    "class": [
                        {
                            "type": {
                                "coding": [
                                    {
                                        "system": "http://terminology.hl7.org/CodeSystem/coverage-class",
                                        "code": "plan",
                                        "display": "Plan",
                                    }
                                ]
                            },
                            "value": "AE303",
                            "name": "Aetna Plan",
                        }
                    ],
                    "network": "Medicare - MA/NY/NJ - Full Reciprocity",
                    "costToBeneficiary": [
                        {
                            "type": {"text": "Annual Physical Exams NMC - In Network"},
                            "valueQuantity": {
                                "value": 50,
                                "unit": "$",
                                "system": "http://aetna.com/Medicare/CostToBeneficiary/ValueQuantity/code",
                            },
                        }
                    ],
                }
            },
        ),
        response=mock_response(
            body=json.dumps(
                {
                    "token_type": "bearer",
                    "access_token": "fake access_token",
                    "expires_in": 54000,
                }
            )
        ),
        timing=times(1),
        file_path=None,
    )

    http = requests.Session()
    http.post(
        mock_server_url + "/" + test_name,
        json={
            "resourceType": "Coverage",
            "id": "aetna-sandbox-3456789012345670303",
            "meta": {
                "source": "http://mock-server:1080/test_patient_access_pipeline/source/4_0_0/Coverage/3456789012345670303",
                "security": [
                    {
                        "system": "https://www.icanbwell.com/owner",
                        "code": "aetna_sandbox",
                    },
                    {
                        "system": "https://www.icanbwell.com/access",
                        "code": "aetna_sandbox",
                    },
                    {
                        "system": "https://www.icanbwell.com/vendor",
                        "code": "aetna_sandbox",
                    },
                    {
                        "system": "https://www.icanbwell.com/connectionType",
                        "code": "proa",
                    },
                ],
            },
            "status": "active",
            "policyHolder": {
                "reference": "Patient/aetna-sandbox-1234567890123456703",
                "type": "Patient",
            },
            "subscriber": {
                "reference": "Patient/aetna-sandbox-1234567890123456703",
                "type": "Patient",
            },
            "beneficiary": {
                "reference": "Patient/aetna-sandbox-1234567890123456703",
                "type": "Patient",
            },
            "payor": [
                {
                    "reference": "Organization/aetna-sandbox-6667778889990000014",
                    "type": "Organization",
                    "display": "Aetna",
                }
            ],
            "identifier": [
                {
                    "type": {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
                                "code": "SN",
                            }
                        ]
                    },
                    "system": "https://sources.aetna.com/coverage/identifier/membershipid/59",
                    "value": "435679010300+AE303+2021-01-01",
                }
            ],
            "type": {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                        "code": "PPO",
                        "display": "preferred provider organization policy",
                    }
                ]
            },
            "subscriberId": "435679010300",
            "relationship": {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/subscriber-relationship",
                        "code": "self",
                    }
                ]
            },
            "period": {"start": "2021-01-01", "end": "2021-12-31"},
            "class": [
                {
                    "type": {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/CodeSystem/coverage-class",
                                "code": "plan",
                                "display": "Plan",
                            }
                        ]
                    },
                    "value": "AE303",
                    "name": "Aetna Plan",
                }
            ],
            "network": "Medicare - MA/NY/NJ - Full Reciprocity",
            "costToBeneficiary": [
                {
                    "type": {"text": "Annual Physical Exams NMC - In Network"},
                    "valueQuantity": {
                        "value": 50,
                        "unit": "$",
                        "system": "http://aetna.com/Medicare/CostToBeneficiary/ValueQuantity/code",
                    },
                }
            ],
        },
    )

    try:
        mock_client.verify_expectations(test_name=test_name)
    except MockServerVerifyException as e:
        print(str(e))
        raise e
