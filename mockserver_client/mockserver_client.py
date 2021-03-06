import collections
import glob
import json
import logging
import os
from logging import Logger
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, cast

import dictdiffer  # type: ignore
from requests import put, Response

from mockserver_client.exceptions.mock_server_exception import (
    MockServerException,
)
from mockserver_client.exceptions.mock_server_expectation_not_found_exception import (
    MockServerExpectationNotFoundException,
)
from mockserver_client.exceptions.mock_server_json_content_mismatch_exception import (
    MockServerJsonContentMismatchException,
)
from mockserver_client.exceptions.mock_server_request_not_found_exception import (
    MockServerRequestNotFoundException,
)
from ._time import _Time
from ._timing import _Timing
from .mock_expectation import MockExpectation
from .mock_request import MockRequest
from .mockserver_verify_exception import MockServerVerifyException


class MockServerFriendlyClient(object):
    """
    Client for the MockServer
    Based on https://pypi.org/project/mockserver-friendly-client/
    """

    def __init__(self, base_url: str) -> None:
        """
        Client for the MockServer
        Based on https://pypi.org/project/mockserver-friendly-client/

        :param base_url: base url to use
        """
        self.base_url: str = base_url
        self.expectations: List[MockExpectation] = []
        self.logger: Logger = logging.getLogger("MockServerClient")
        self.logger.setLevel(os.environ.get("LOGLEVEL") or logging.INFO)

    def _call(self, command: str, data: Any = None) -> Response:
        return put("{}/{}".format(self.base_url, command), data=data)

    def clear(self, path: str) -> None:
        """
        Clear all data related to this path


        :param path:
        """
        self.expectations = []
        self._call("clear", json.dumps({"path": path}))

    def reset(self) -> None:
        """
        Clear all data in the MockServer

        """
        self.expectations = []
        self._call("reset")

    def stub(
        self,
        request1: Any,
        response1: Any,
        timing: Any = None,
        time_to_live: Any = None,
    ) -> None:
        """
        Create an expectation in mock server


        :param request1: mock request
        :param response1: mock response
        :param timing: how many times to expect the request
        :param time_to_live:
        """
        self._call(
            "expectation",
            json.dumps(
                _non_null_options_to_dict(
                    _Option("httpRequest", request1),
                    _Option("httpResponse", response1),
                    _Option("times", (timing or _Timing()).for_expectation()),
                    _Option("timeToLive", time_to_live, formatter=_to_time_to_live),
                )
            ),
        )

    def expect(
        self,
        request1: Dict[str, Any],
        response1: Dict[str, Any],
        timing: _Timing,
        time_to_live: Any = None,
    ) -> None:
        """
        Expect this mock request and reply with the provided mock response


        :param request1: mock request
        :param response1: mock response
        :param timing: how many times to expect the request
        :param time_to_live:
        """
        self.stub(request1, response1, timing, time_to_live)
        self.expectations.append(
            MockExpectation(request=request1, response=response1, timing=timing)
        )

    def expect_files_as_requests(
        self,
        folder: Path,
        url_prefix: Optional[str],
        content_type: str = "application/fhir+json",
        add_file_name: bool = False,
    ) -> List[str]:
        """
        Read the files in the specified folder and create mock requests for each file


        :param folder: folder to read the files from
        :param url_prefix: url_prefix to use when mocking requests
        :param content_type: content type to use for requests
        :param add_file_name: whether to add the file name to the url
        :return: list of files read
        """
        file_path: str
        files: List[str] = sorted(
            glob.glob(str(folder.joinpath("**/*.json")), recursive=True)
        )
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

                path = f"{('/' + url_prefix) if url_prefix else ''}"
                path = (
                    f"{path}/{os.path.splitext(file_name)[0]}"
                    if add_file_name
                    else path
                )

                try:
                    request_result = content["request_result"]
                except ValueError:
                    raise Exception(
                        "`request_result` key not found. It is supposed to contain the expected result of the requst function."
                    )
                body = (
                    json.dumps(request_result)
                    if content_type == "application/fhir+json"
                    else request_result
                )
                self.expect(
                    mock_request(path=path, **request_parameters),
                    mock_response(body=body),
                    timing=times(1),
                )
                self.logger.info(f"Mocking {self.base_url}{path}: {request_parameters}")
        return files

    def expect_files_as_json_requests(
        self,
        folder: Path,
        path: str,
        json_response_body: Dict[str, Any],
        add_file_name: bool = False,
    ) -> List[str]:
        """
        Read the files in the specified folder and create mock requests for each file


        :param folder: folder to read the files from
        :param path: url_prefix to use when mocking requests
        :param json_response_body: mock response body to return for each mock request
        :param add_file_name: whether to add the file name to the url
        :return: list of files read
        """
        file_path: str
        files: List[str] = sorted(
            glob.glob(str(folder.joinpath("**/*.json")), recursive=True)
        )
        for file_path in files:
            file_name = os.path.basename(file_path)
            with open(file_path, "r") as file:
                content: Dict[str, Any] = json.loads(file.read())
                path = (
                    f"{path}/{os.path.splitext(file_name)[0]}"
                    if add_file_name
                    else path
                )
                self.expect(
                    mock_request(path=path, body=json_equals([content]), method="POST"),
                    mock_response(body=json.dumps(json_response_body)),
                    timing=times(1),
                )
                self.logger.info(f"Mocking {self.base_url}{path}")
        return files

    def expect_default(
        self,
    ) -> None:
        """
        Fallback handler for all requests


        """
        response1: Dict[str, Any] = mock_response()
        timing: _Timing = times_any()
        self.stub({}, response1, timing, None)
        self.expectations.append(MockExpectation({}, {}, timing))

    def match_to_recorded_requests(
        self,
        recorded_requests: List[MockRequest],
    ) -> List[MockServerException]:
        """
        Matches recorded requests with expected requests
        There are 4 cases possible:
        1. There was an expectation without a corresponding request -> fail
        2. There was a request without a corresponding expectation -> save request as expectation
        3. There was a matching request and expectation but the content did not match -> error and show diff
        4. There was a matching request and expectation and the content matched -> nothing to do


        :param recorded_requests: list of requests actually made to the mock server
        :return: list of match exceptions
        """
        exceptions: List[MockServerException] = []
        unmatched_expectation_requests: List[MockRequest] = []
        unmatched_requests: List[MockRequest] = [r for r in recorded_requests]
        expected_request: MockRequest
        self.logger.debug("-------- EXPECTATIONS --------")
        expectation: MockExpectation
        for expectation in self.expectations:
            self.logger.debug(expectation)
        self.logger.debug("-------- END EXPECTATIONS --------")
        self.logger.debug("-------- REQUESTS --------")
        recorded_request: MockRequest
        for recorded_request in recorded_requests:
            self.logger.debug(recorded_request)
        self.logger.debug("-------- END REQUESTS --------")

        # get ids of all recorded requests
        recorded_request_ids: List[str] = []
        for recorded_request in recorded_requests:
            json1: Optional[List[Dict[str, Any]]] = recorded_request.json_list
            if json1:
                # get ids from body and match
                # see if the property is string
                # noinspection PyTypeChecker
                json1_id_list: List[str] = [j["id"] for j in json1 if "id" in j]
                for j in json1_id_list:
                    recorded_request_ids.append(j)

        # now try to match requests to expectations
        for expectation in self.expectations:
            expected_request = expectation.request
            found_expectation: bool = False
            try:
                found_expectation = self.find_matches_on_request_and_body(
                    expected_request=expected_request,
                    recorded_requests=recorded_requests,
                    unmatched_requests=unmatched_requests,
                )
                if not found_expectation:
                    found_expectation = self.find_matches_on_request_url_only(
                        expected_request=expected_request,
                        recorded_requests=recorded_requests,
                        unmatched_requests=unmatched_requests,
                    )
            except MockServerJsonContentMismatchException as e:
                exceptions.append(e)
            if not found_expectation and expected_request.method:
                unmatched_expectation_requests.append(expected_request)
                self.logger.info("---- EXPECTATION NOT MATCHED ----")
                self.logger.info(f"{expected_request}")
                self.logger.info("IDs sent in requests")
                self.logger.info(f'{",".join(recorded_request_ids)}')
                self.logger.info("---- END EXPECTATION NOT MATCHED ----")
        # now fail for every expectation in unmatched_expectation_requests
        for unmatched_expectation in unmatched_expectation_requests:
            exceptions.append(
                MockServerExpectationNotFoundException(
                    url=unmatched_expectation.path,
                    json_list=unmatched_expectation.json_list,
                    querystring_params=unmatched_expectation.querystring_params,
                )
            )
        # and for every request in unmatched_requests
        for unmatched_request in unmatched_requests:
            exceptions.append(
                MockServerRequestNotFoundException(
                    method=unmatched_request.method,
                    url=unmatched_request.path,
                    json_list=unmatched_request.json_list,
                )
            )
        return exceptions

    def find_matches_on_request_url_only(
        self,
        *,
        expected_request: MockRequest,
        recorded_requests: List[MockRequest],
        unmatched_requests: List[MockRequest],
    ) -> bool:
        """
        Finds matches on url only and then compares the bodies.  Returns if match was found.
        Throws a JsonContentMismatchException if a url match was found but no body match was found


        :param expected_request: request that was expected
        :param recorded_requests: list of all requests made
        :param unmatched_requests: list of requests that have not been matched to an expectation
        :return: whether a matching expectation was found
        """
        found_expectation: bool = False
        recorded_request: MockRequest
        for recorded_request in recorded_requests:
            if expected_request.method and self.does_request_match(
                request1=expected_request,
                request2=recorded_request,
                check_body=False,
            ):
                # find all requests that match on url since there can be multiple
                # and then check if the bodies match
                # matching_expectations = [
                #     m
                #     for m in self.expectations
                #     if "method" in m.request
                #     and self.does_request_match(
                #         request1=m.request,
                #         request2=recorded_request,
                #         check_body=False,
                #     )
                # ]
                found_expectation = True
                # remove request from unmatched_requests
                unmatched_request_list = [
                    r
                    for r in unmatched_requests
                    if self.does_request_match(
                        request1=r, request2=recorded_request, check_body=True
                    )
                ]
                if expected_request.json_list:
                    expected_body_json: Optional[
                        List[Dict[str, Any]]
                    ] = expected_request.json_list
                    actual_body_json: Optional[
                        List[Dict[str, Any]]
                    ] = recorded_request.json_list
                    assert len(unmatched_request_list) < 2, (
                        f"Found {len(unmatched_request_list)}"
                        f" unmatched requests for {recorded_request}"
                    )
                    if len(unmatched_request_list) > 0:
                        unmatched_requests.remove(unmatched_request_list[0])
                    self.compare_request_bodies_json(
                        actual_body_json, expected_body_json
                    )
                elif expected_request.body_list:
                    if len(unmatched_request_list) > 0:
                        unmatched_requests.remove(unmatched_request_list[0])
                    self.compare_request_bodies(
                        recorded_request.body_list, expected_request.body_list
                    )
        return found_expectation

    def find_matches_on_request_and_body(
        self,
        *,
        expected_request: MockRequest,
        recorded_requests: List[MockRequest],
        unmatched_requests: List[MockRequest],
    ) -> bool:
        """
        Matches on both request and body and returns whether it was able to find a match


        :param expected_request: request that was expected
        :param recorded_requests: list of all requests made
        :param unmatched_requests: list of requests that have not been matched to an expectation
        :return: whether a matching expectation was found
        """
        # first try to find all exact matches on both request url and body
        found_expectation: bool = False
        for recorded_request in recorded_requests:
            # first try to match on both request url AND body
            # If match is found then remove this request from list of unmatched requests
            if expected_request.method and self.does_request_match(
                request1=expected_request,
                request2=recorded_request,
                check_body=True,
            ):
                found_expectation = True
                # remove request from unmatched_requests
                unmatched_request_list = [
                    r
                    for r in unmatched_requests
                    if self.does_request_match(
                        request1=r, request2=recorded_request, check_body=True
                    )
                ]
                assert (
                    len(unmatched_request_list) >= 0
                ), f"{','.join([str(c) for c in unmatched_request_list])}"
                if len(unmatched_request_list) > 0:
                    unmatched_requests.remove(unmatched_request_list[0])

            # now try to find matches on just url
        return found_expectation

    @staticmethod
    def does_request_match(
        request1: MockRequest, request2: MockRequest, check_body: bool
    ) -> bool:
        """
        Does request1 match request2

        :param request1: request 1
        :param request2: request 2
        :param check_body: whether to match the body or not
        :return: whether the two requests match
        """
        return (
            request1.method == request2.method
            and request1.path == request2.path
            and MockServerFriendlyClient.normalize_querystring_params(
                request1.querystring_params
            )
            == MockServerFriendlyClient.normalize_querystring_params(
                request2.querystring_params
            )
            and MockServerFriendlyClient.does_id_in_request_match(
                request1=request1, request2=request2
            )
            and (
                not check_body
                or MockServerFriendlyClient.does_request_body_match(
                    request1=request1, request2=request2
                )
            )
        )

    @staticmethod
    def does_request_body_match(request1: MockRequest, request2: MockRequest) -> bool:
        """
        Does the body of the two specified requests match

        :param request1: request 1
        :param request2: request 2
        :return: whether the body of the two specified requests match
        :rtype:
        """
        if not request1.body_list and not request2.body_list:
            return True
        if request1.body_list and not request2.body_list:
            return False
        if request2.body_list and not request1.body_list:
            return False
        if request1.json_list and request2.json_list:
            return True if request1.json_list == request2.json_list else False
        return True if request1.body_list == request2.body_list else False

    @staticmethod
    def does_id_in_request_match(request1: MockRequest, request2: MockRequest) -> bool:
        """
        Whether the id in the two specified requests match.


        :param request1: request 1
        :param request2: request 2
        :return: Whether the id in the two specified requests match.
        """
        json1_list: Optional[List[Dict[str, Any]]] = request1.json_list
        json2_list: Optional[List[Dict[str, Any]]] = request2.json_list

        if json1_list and json2_list:
            # get ids from body and match
            # see if the property is string
            json1_id_list: List[str] = [j["id"] for j in json1_list if "id" in j]
            json2_id_list: List[str] = [j["id"] for j in json2_list if "id" in j]
            return True if json1_id_list == json2_id_list else False
        elif json1_list is None and json2_list is None:
            return True
        else:
            return False

    @staticmethod
    def compare_request_bodies(
        actual_body_list: Optional[List[Dict[str, Any]]],
        expected_body_list: Optional[List[Dict[str, Any]]],
    ) -> None:
        """
        Compares the bodies of the two requests and raises an exception with detailed diff if they don't match


        :param actual_body_list: body of actual request
        :param expected_body_list: body of expected request
        """
        differences = list(dictdiffer.diff(expected_body_list, actual_body_list))
        if len(differences) > 0:
            raise MockServerJsonContentMismatchException(
                actual_json=actual_body_list,
                expected_json=expected_body_list,
                differences=differences,
                expected_file_path=Path(),
            )

    @staticmethod
    def compare_request_bodies_json(
        actual_json: Optional[List[Dict[str, Any]]],
        expected_json: Optional[List[Dict[str, Any]]],
    ) -> None:
        """
        Compares the JSON bodies of the two requests and raises an exception with detailed diff if they don't match

        :param actual_json: json of actual request
        :param expected_json: json of expected request
        """
        differences = list(dictdiffer.diff(expected_json, actual_json))
        if len(differences) > 0:
            raise MockServerJsonContentMismatchException(
                actual_json=actual_json,
                expected_json=expected_json,
                differences=differences,
                expected_file_path=Path(),
            )

    def verify_expectations(
        self, test_name: Optional[str] = None, files: Optional[List[str]] = None
    ) -> None:
        """
        Verify that the requests made match the expectations.  Raises exceptions if there are mismatches


        :param test_name: Name of test
        :param files: files to create expectations
        """
        recorded_requests: List[MockRequest] = self.retrieve_requests()
        self.logger.debug(f"Count of retrieved requests: {len(recorded_requests)}")
        self.logger.debug("-------- All Retrieved Requests -----")
        for recorded_request in recorded_requests:
            self.logger.debug(f"{recorded_request}")
        self.logger.debug("-------- End All Retrieved Requests -----")
        # now filter to the requests for this test only
        if test_name is not None:
            recorded_requests = [
                r for r in recorded_requests if r.path and test_name in r.path
            ]
        self.logger.debug(
            f"Count of recorded requests for test: {len(recorded_requests)}"
        )
        exceptions: List[MockServerException] = self.match_to_recorded_requests(
            recorded_requests=recorded_requests
        )
        if len(exceptions) > 0:
            raise MockServerVerifyException(exceptions=exceptions, files=files)

    def retrieve_requests(self) -> List[MockRequest]:
        """
        Retrieve requests made to mock server


        :return: list of requests made to mock server
        """
        result = self._call("retrieve")
        # https://app.swaggerhub.com/apis/jamesdbloom/mock-server-openapi/5.11.x#/control/put_retrieve
        raw_requests: List[Dict[str, Any]] = cast(
            List[Dict[str, Any]], json.loads(result.text)
        )
        return [MockRequest(request=r) for r in raw_requests]

    @staticmethod
    def normalize_querystring_params(
        querystring_params: Optional[Union[List[Dict[str, Any]], Dict[str, Any]]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        ensure a dictionary of querystring params is formatted so that the param name is the dictionary key.
        querystring dictionaries from requests sometimes look like this. don't want that.
        "queryStringParameters": [
            {
                "name": "contained",
                "values": [
                    "true"
                ]
            },
            {
                "name": "id",
                "values": [
                    "1023011178"
                ]
            }
        ],
        """
        if querystring_params is None:
            return None
        if type(querystring_params) is dict:
            return querystring_params

        normalized_params: Dict[str, Any] = {}
        for param_dict in querystring_params:
            params: Dict[str, Any] = param_dict  # type: ignore
            normalized_params[params["name"]] = params["values"]
        return normalized_params


def mock_request(
    method: Optional[str] = None,
    path: Optional[str] = None,
    querystring: Optional[Dict[str, Any]] = None,
    body: Optional[Union[str, Dict[str, Any]]] = None,
    headers: Optional[Dict[str, Any]] = None,
    cookies: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Mocks a request


    :param method: method of request
    :param path: path of request (No query strings in path.  Use the querystring parameter)
    :param querystring: dict of query strings
    :param body: body to expect in the request
    :param headers: headers to expect in the request
    :param cookies: cookies to expect in the request
    :return: mock request
    """
    assert (
        not path or "?" not in path
    ), "Do not specify query string in the path.  Use the querystring parameter"

    return _non_null_options_to_dict(
        _Option("method", method),
        _Option("path", path),
        _Option("queryStringParameters", querystring, formatter=_to_named_values_list),
        _Option("body", body),
        _Option("headers", headers, formatter=_to_named_values_list),
        _Option("cookies", cookies),
    )


def mock_response(
    code: Optional[int] = None,
    body: Optional[Union[str, Dict[str, Any]]] = None,
    headers: Optional[Dict[str, Any]] = None,
    cookies: Optional[str] = None,
    delay: Optional[str] = None,
    reason: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Specifies the mock response for a mock request


    :param code: code to return in mock response
    :param body: body to return in mock response
    :param headers: headers to return in mock response
    :param cookies: cookies to return in mock response
    :param delay: delay to use before returning response
    :param reason: reason phrase to return in mock response
    :return: mock response
    """
    return _non_null_options_to_dict(
        _Option("statusCode", code),
        _Option("reasonPhrase", reason),
        _Option("body", body),
        _Option("headers", headers, formatter=_to_named_values_list),
        _Option("delay", delay, formatter=_to_delay),
        _Option("cookies", cookies),
    )


def times(count: int) -> _Timing:
    """
    How many times to expect the request


    :param count: count
    :return: Timing object
    """
    return _Timing(count)


def times_once() -> _Timing:
    """
    Expect the request a single time


    :return: Timing object
    """
    return _Timing(1)


def times_any() -> _Timing:
    """
    Expect the request unlimited number of times


    :return: Timing object
    """
    return _Timing()


def form(form1: Any) -> Dict[str, Any]:
    # NOTE(lindycoder): Support for mockservers version before https://github.com/jamesdbloom/mockserver/issues/371
    return collections.OrderedDict(
        (("type", "PARAMETERS"), ("parameters", _to_named_values_list(form1)))
    )


def json_equals(payload: Union[Dict[str, Any], List[Dict[str, Any]]]) -> Dict[str, Any]:
    """
    Expects that the request payload is equal to the given payload.

    :param payload: json to compare to
    :return:
    """
    return collections.OrderedDict(
        (("type", "JSON"), ("json", json.dumps(payload)), ("matchType", "STRICT"))
    )


def text_equals(payload: str) -> Dict[str, Any]:
    """
    Expects that the request payload is equal to the given payload.

    :param payload: text to compare to
    :return:
    """
    return collections.OrderedDict(
        (
            ("type", "STRING"),
            ("string", payload),
            ("contentType", "text/plain; charset=utf-8"),
        )
    )


def json_contains(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Expects the request payload to match all given fields. The request may have more fields.


    :param payload: returned json must include this
    :return:
    """
    return collections.OrderedDict(
        (
            ("type", "JSON"),
            ("json", json.dumps(payload)),
            ("matchType", "ONLY_MATCHING_FIELDS"),
        )
    )


def json_response(
    body: Any = None, headers: Any = None, **kwargs: Any
) -> Dict[str, Any]:
    """
    Expect this json response


    :param body:
    :param headers:
    :param kwargs:
    :return:
    """
    headers = headers or {}
    headers["Content-Type"] = "application/json"
    return mock_response(body=json.dumps(body), headers=headers, **kwargs)


class _Option:
    def __init__(self, field: Any, value: Any, formatter: Any = None) -> None:
        self.field = field
        self.value = value
        self.formatter = formatter or (lambda e: e)


def seconds(value: int) -> _Time:
    return _Time("SECONDS", value)


def milliseconds(value: int) -> _Time:
    return _Time("MILLISECONDS", value)


def microseconds(value: int) -> _Time:
    return _Time("MICROSECONDS", value)


def nanoseconds(value: int) -> _Time:
    return _Time("NANOSECONDS", value)


def minutes(value: int) -> _Time:
    return _Time("MINUTES", value)


def hours(value: int) -> _Time:
    return _Time("HOURS", value)


def days(value: int) -> _Time:
    return _Time("DAYS", value)


def _non_null_options_to_dict(*options: Any) -> Dict[str, Any]:
    return {o.field: o.formatter(o.value) for o in options if o.value is not None}


def _to_named_values_list(dictionary: Dict[str, Any]) -> List[Dict[str, Any]]:
    return [{"name": key, "values": [value]} for key, value in dictionary.items()]


def _to_time(value: Union[_Time, int]) -> _Time:
    if not isinstance(value, _Time):
        value = seconds(value)
    return value


def _to_delay(delay: _Time) -> Dict[str, Any]:
    delay = _to_time(delay)
    return {"timeUnit": delay.unit, "value": delay.value}


def _to_time_to_live(time: Union[_Time, int]) -> Dict[str, Any]:
    time = _to_time(time)
    return {"timeToLive": time.value, "timeUnit": time.unit, "unlimited": False}
