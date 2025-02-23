import json
import os
from glob import glob
from pathlib import Path
from typing import Dict, Any, List, Optional

from mockserver_client.error_messages import common_error_messages
from mockserver_client.mockserver_client import (
    mock_request,
    mock_response,
    MockServerFriendlyClient,
    json_equals,
    times,
    text_equals,
)


def load_mock_fhir_requests_from_folder(
    folder: Path,
    mock_client: MockServerFriendlyClient,
    method: str = "POST",
    relative_path: Optional[str] = None,
    query_string: Optional[Dict[str, Any]] = None,
    url_prefix: Optional[str] = None,
    response_body: Optional[str] = None,
) -> List[str]:
    """
    Loads all .json files from the folder and its sub-folders

    from https://pypi.org/project/mockserver-friendly-client/

    :param folder: where to look for .json files (recursively)
    :param mock_client: client to mock server
    :param method:
    :param relative_path:
    :param query_string:
    :param url_prefix:
    :param response_body:
    """
    file_path: str
    files: List[str] = sorted(
        glob(str(folder.joinpath("**/*.json")), recursive=True), reverse=True
    )
    for file_path in files:
        # load file as json
        with open(file_path, "r") as file:
            contents = json.loads(file.read())
            if isinstance(contents, list) and not relative_path:
                for fhir_request in contents:
                    mock_single_request(
                        fhir_request=fhir_request,
                        method=method,
                        mock_client=mock_client,
                        relative_path=relative_path,
                        query_string=query_string,
                        url_prefix=url_prefix,
                        response_body=response_body,
                        file_path=file_path,
                    )
            elif contents.get("resourceType") == "Bundle" and contents.get("entry"):
                mock_bundle_request(
                    fhir_request=contents,
                    method=method,
                    mock_client=mock_client,
                    relative_path=relative_path,
                    query_string=query_string,
                    url_prefix=url_prefix,
                    response_body=response_body,
                    bundle=contents,
                    file_path=file_path,
                )
            else:
                mock_single_request(
                    fhir_request=contents,
                    method=method,
                    mock_client=mock_client,
                    relative_path=relative_path,
                    query_string=query_string,
                    url_prefix=url_prefix,
                    response_body=response_body,
                    file_path=file_path,
                )

    return files


def load_mock_fhir_requests_for_single_file(
    folder: Path,
    single_file_name: str,
    mock_client: MockServerFriendlyClient,
    method: str = "POST",
    relative_path: Optional[str] = None,
    query_string: Optional[Dict[str, Any]] = None,
    url_prefix: Optional[str] = None,
    response_body: Optional[str] = None,
) -> List[str]:
    """
    Loads a single .json file from the given folder

    from https://pypi.org/project/mockserver-friendly-client/

    :param folder: where to look for a given .json file
    :param single_file_name: a single json file name
    :param mock_client: client to mock server
    :param method:
    :param relative_path:
    :param query_string:
    :param url_prefix:
    :param response_body:
    """

    file_path: str
    files: List[str] = sorted(
        glob(str(folder.joinpath(f"**/{single_file_name}")), recursive=True)
    )
    for file_path in files:
        # load file as json
        with open(file_path, "r") as file:
            contents = json.loads(file.read())

            mock_single_request(
                fhir_request=contents,
                method=method,
                mock_client=mock_client,
                relative_path=relative_path,
                query_string=query_string,
                url_prefix=url_prefix,
                response_body=response_body,
                file_path=file_path,
            )

    return files


def mock_single_request(
    fhir_request: Dict[str, Any],
    method: str,
    mock_client: MockServerFriendlyClient,
    relative_path: Optional[str],
    query_string: Optional[Dict[str, Any]],
    url_prefix: Optional[str],
    response_body: Optional[str],
    file_path: Optional[str],
) -> None:
    # find id and resourceType
    if method == "POST":
        # id_ = fhir_request["id"]
        # noinspection PyPep8Naming
        resourceType = fhir_request["resourceType"]
        id_ = fhir_request["id"]
        path = f"{('/' + url_prefix) if url_prefix else ''}/4_0_0/{resourceType}/{id_}/$merge"
        payload: str = (
            json.dumps(
                [
                    {
                        "id": id_,
                        "updated": False,
                        "created": True,
                        "resourceType": resourceType,
                    }
                ]
            )
            if not response_body
            else response_body
        )
        mock_client.expect(
            request=mock_request(
                method="POST",
                path=path,
                body=json_equals(fhir_request),
            ),
            response=mock_response(body=payload),
            timing=times(1),
            file_path=file_path,
        )
    elif method == "PUT":
        id_ = fhir_request["id"]
        # noinspection PyPep8Naming
        resourceType = fhir_request["resourceType"]
        path = f"{('/' + url_prefix) if url_prefix else ''}/4_0_0/{resourceType}/{id_}"

        payload = (
            json.dumps(
                [
                    {
                        "id": id_,
                        "updated": True,
                        "created": False,
                        "resourceType": resourceType,
                    }
                ]
            )
            if not response_body
            else response_body
        )

        mock_client.expect(
            request=mock_request(
                method="PUT",
                path=path,
                body=json_equals(fhir_request),
            ),
            response=mock_response(body=payload),
            timing=times(1),
            file_path=file_path,
        )
    else:
        if not relative_path:
            id_ = fhir_request["id"]
            # noinspection PyPep8Naming
            resourceType = fhir_request["resourceType"]
            path = (
                f"{('/' + url_prefix) if url_prefix else ''}/4_0_0/{resourceType}/{id_}"
            )
            mock_client.expect(
                request=mock_request(method="GET", path=path, querystring=query_string),
                response=mock_response(body=json.dumps(fhir_request)),
                timing=times(1),
                file_path=file_path,
            )
        else:
            path = f"{('/' + url_prefix) if url_prefix else ''}/4_0_0/{relative_path}"
            mock_client.expect(
                request=mock_request(method="GET", path=path, querystring=query_string),
                response=mock_response(body=json.dumps(fhir_request)),
                timing=times(1),
                file_path=file_path,
            )


def mock_bundle_request(
    fhir_request: Dict[str, Any],
    method: str,
    mock_client: MockServerFriendlyClient,
    relative_path: Optional[str],
    query_string: Optional[Dict[str, Any]],
    url_prefix: Optional[str],
    response_body: Optional[str],
    bundle: Dict[str, Any],
    file_path: Optional[str],
) -> None:
    # find id and resourceType
    if method == "POST":
        id_ = fhir_request["id"] or "1"
        # noinspection PyPep8Naming
        resourceType = fhir_request["resourceType"]
        path = f"{('/' + url_prefix) if url_prefix else ''}/4_0_0/{resourceType}/{id_}/$merge"
        bundle_entries = bundle.get("entry")
        payload: str = (
            json.dumps(
                [
                    {
                        "id": entry.get("resource", {}).get("id", ""),
                        "updated": False,
                        "created": True,
                        "resourceType": entry.get("resource", {}).get(
                            "resourceType", ""
                        ),
                    }
                    for entry in bundle_entries
                ]
                if bundle_entries
                else []
            )
            if not response_body
            else response_body
        )
        mock_client.expect(
            request=mock_request(
                method="POST",
                path=path,
                body=json_equals(fhir_request),
            ),
            response=mock_response(body=payload),
            timing=times(1),
            file_path=file_path,
        )
    else:
        if not relative_path:
            id_ = fhir_request["id"]
            # noinspection PyPep8Naming
            resourceType = fhir_request["resourceType"]
            path = (
                f"{('/' + url_prefix) if url_prefix else ''}/4_0_0/{resourceType}/{id_}"
            )
            mock_client.expect(
                request=mock_request(method="GET", path=path, querystring=query_string),
                response=mock_response(body=json.dumps(fhir_request)),
                timing=times(1),
                file_path=file_path,
            )
        else:
            path = f"{('/' + url_prefix) if url_prefix else ''}/4_0_0/{relative_path}"
            mock_client.expect(
                request=mock_request(method="GET", path=path, querystring=query_string),
                response=mock_response(body=json.dumps(fhir_request)),
                timing=times(1),
                file_path=file_path,
            )


# noinspection PyPep8Naming
def load_mock_fhir_everything_requests_from_folder(
    folder: Path,
    mock_client: MockServerFriendlyClient,
    resourceType: str,
    url_prefix: Optional[str] = None,
) -> List[str]:
    """
    Loads all .json files from the folder and its sub-folders

    from https://pypi.org/project/mockserver-friendly-client/

    :param folder: where to look for .json files (recursively)
    :param mock_client:
    :param resourceType:
    :param url_prefix:
    """
    file_path: str
    files: List[str] = glob(str(folder.joinpath("**/*.json")), recursive=True)
    for file_path in files:
        # load file as json
        with open(file_path, "r") as file:
            fhir_request: Dict[str, Any] = json.loads(file.read())
            # find id and resourceType
            id_: str = fhir_request["id"]
            path = f"{('/' + url_prefix) if url_prefix else ''}/4_0_0/{resourceType}/{id_}/$everything"
            mock_client.expect(
                request=mock_request(
                    method="GET",
                    path=path,
                ),
                response=mock_response(body=json.dumps(fhir_request)),
                timing=times(1),
                file_path=file_path,
            )
    return files


# noinspection PyPep8Naming
def load_mock_fhir_everything_batch_requests_from_folder(
    folder: Path,
    mock_client: MockServerFriendlyClient,
    resourceType: str,
    ids: List[str],
    url_prefix: Optional[str] = None,
) -> List[str]:
    """
    Loads all .json files from the folder and its sub-folders

    from https://pypi.org/project/mockserver-friendly-client/

    :param folder: where to look for .json files (recursively)
    :param mock_client:
    :param resourceType:
    :param url_prefix:
    :param ids: id of resources for this batch to load
    """
    file_path: str
    files: List[str] = glob(str(folder.joinpath("**/*.json")), recursive=True)
    result_bundle = {
        "resourceType": "Bundle",
        "id": "bundle-example",
        "type": "collection",
        "entry": [],
    }
    print(f"mock fhir batch request for {ids}")
    for file_path in files:
        with open(file_path, "r") as file:
            fhir_bundle: Dict[str, Any] = json.loads(file.read())
        if "entry" not in fhir_bundle:
            print(f"{file_path} has no entry property!")
            continue
        for entry in fhir_bundle["entry"]:
            id_ = entry.get("resource", {}).get("id", "")
            if id_ in ids:
                result_bundle["entry"].append(entry)  # type: ignore
    # find id and resourceType
    path = (
        f"{('/' + url_prefix) if url_prefix else ''}/4_0_0/{resourceType}/$everything"
    )
    mock_client.expect(
        request=mock_request(
            method="GET", path=path, querystring={"id": ",".join(ids)}
        ),
        response=mock_response(body=json.dumps(result_bundle)),
        timing=times(1),
        file_path=files[0] if files else None,
    )
    return files


def load_mock_elasticsearch_requests_from_folder(
    folder: Path, mock_client: MockServerFriendlyClient, index: str
) -> List[str]:
    """
    Loads all .json files from the folder and its sub-folders

    from https://pypi.org/project/mockserver-friendly-client/

    :param folder: where to look for .json files (recursively)
    :param mock_client:
    :param index:
    """
    file_path: str
    files: List[str] = glob(str(folder.joinpath("**/*.json")), recursive=True)
    for file_path in files:
        # load file as json
        with open(file_path, "r") as file:
            lines: List[str] = file.readlines()
            http_request: str = "\n".join(
                [
                    (json.dumps(json.loads(line))) if line != "\n" else ""
                    for line in lines
                ]
            )
            # noinspection PyPep8Naming
            path = f"/{index}/_bulk"
            # noinspection SpellCheckingInspection
            mock_client.expect(
                request=mock_request(
                    method="POST",
                    path=path,
                    body=text_equals(http_request),
                ),
                response=mock_response(
                    headers={"Content-Type": "application/json"},
                    body=f"""
{{
    "took": 194,
    "errors": false,
    "items": [
        {{
            "index": {{
                "_index": "{index}",
                "_type": "_doc",
                "_id": "TESQ93YBW4SQ_M9deEJw",
                "_version": 1,
                "result": "created"
            }}
        }},
        {{
            "index": {{
                "_index": "{index}",
                "_type": "_doc",
                "_id": "TUSQ93YBW4SQ_M9deEJw",
                "_version": 1,
                "result": "created"
            }}
        }}
    ]
}}""",
                ),
                timing=times(1),
                file_path=file_path,
            )
    return files


def load_mock_source_api_responses_from_folder(
    folder: Path,
    mock_client: MockServerFriendlyClient,
    url_prefix: Optional[str],
    times_: int = 1,
) -> List[str]:
    """
    Mock responses for all files from the folder and its sub-folders

    from https://pypi.org/project/mockserver-friendly-client/

    :param folder: where to look for files (recursively)
    :param mock_client: client to mock server
    :param url_prefix: http://{mock_server_url}/{url_prefix}...
    :param times_: number of times to mock the response
    """
    file_path: str
    files: List[str] = sorted(glob(str(folder.joinpath("**/*")), recursive=True))
    for file_path in files:
        with open(file_path, "r") as file:
            content = file.read()
            path = f"{('/' + url_prefix) if url_prefix else ''}/{os.path.basename(file_path)}"
            mock_client.expect(
                request=mock_request(
                    method="GET",
                    path=path,
                ),
                response=mock_response(body=content),
                timing=times(times_),
                file_path=file_path,
            )
    return files


def load_mock_source_api_json_responses(
    folder: Path,
    mock_client: MockServerFriendlyClient,
    url_prefix: Optional[str],
    add_file_name: Optional[bool] = False,
    url_suffix: Optional[str] = None,
    times_: int = 1,
) -> List[str]:
    """
    Mock responses for all files from the folder and its sub-folders

    :param folder: where to look for files (recursively)
    :param mock_client:
    :param url_prefix: http://{mock_server_url}/{url_prefix}...
    :param add_file_name: http://{mock_server_url}/{url_prefix}/{add_file_name}...
    :param url_suffix: http://{mock_server_url}/{url_prefix}/{add_file_name}/{url_suffix}?
    :param times_: number of times to mock the response
    """
    file_path: str
    files: List[str] = sorted(glob(str(folder.joinpath("**/*.json")), recursive=True))
    for file_path in files:
        file_name = os.path.basename(file_path)
        with open(file_path, "r") as file:
            content = json.loads(file.read())

            try:
                request_parameters = content["request_parameters"]
            except ValueError:
                raise Exception(
                    "`request_parameters` key not found! It is supposed to contain parameters of the request function."
                )

            if "path" in request_parameters:
                if not request_parameters["path"].startswith("/"):
                    path = f"{('/' + url_prefix) if url_prefix else ''}"
                    path = f"{path}/{request_parameters['path']}"
                else:
                    path = request_parameters["path"]
                del request_parameters["path"]
            else:
                path = f"{('/' + url_prefix) if url_prefix else ''}"
                path = (
                    f"{path}/{os.path.splitext(file_name)[0]}"
                    if add_file_name
                    else path
                )
                if url_suffix:
                    path = f"{path}/{url_suffix}"

            if "description" in request_parameters:
                description = request_parameters["description"]
                del request_parameters["description"]
                if request_parameters.get("headers"):
                    request_parameters["headers"]["X-Description"] = description
                else:
                    request_parameters["headers"] = {"X-Description": description}

            try:
                request_result = content["request_result"]
                response_parameters: Dict[str, Any] = {}
                if "statusCode" in request_result:
                    code = int(request_result["statusCode"])
                    request_result.pop("statusCode")
                    # If request_result is empty, then add the generic error response
                    if not request_result and (int(code) >= 400):
                        request_result["error_message"] = (
                            f"HTTP {code} ERROR: {common_error_messages.get(int(code), 'Unknown status code')}"
                        )
                    response_parameters["code"] = code
                if "headers" in request_result:
                    headers = request_result["headers"]
                    assert isinstance(
                        headers, dict
                    ), f"headers should be a dictionary: {headers}"
                    request_result.pop("headers")
                    response_parameters["headers"] = headers
                if "body" in request_result:
                    raw_body = request_result["body"]
                    assert isinstance(
                        raw_body, str
                    ), f"body should be a string: {raw_body}"
                    response_parameters["body"] = raw_body
                else:
                    response_parameters["body"] = json.dumps(request_result)
                if "connectionOptions" in request_result:
                    connection_options = request_result["connectionOptions"]
                    assert isinstance(
                        connection_options, dict
                    ), f"connectionOptions should be a dictionary: {connection_options}"
                    request_result.pop("connectionOptions")
                    response_parameters["connectionOptions"] = connection_options
                # now mock it
                mock_client.expect(
                    request=mock_request(path=path, **request_parameters),
                    response=mock_response(**response_parameters),
                    timing=times(times_),
                    file_path=file_path,
                )
            except ValueError:
                raise Exception(
                    "`request_result` key not found. "
                    + "It is supposed to contain the expected result of the request function."
                )

    return files
