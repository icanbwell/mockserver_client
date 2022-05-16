import json
import logging
import os
from logging import Logger
import string
import random
from typing import Any, Dict, List, Optional, Union

from requests import put, Response

from ._time import _Time
from ._timing import _Timing
from .mock_expectation import MockExpectation


class MockServerFriendlyClientIdx(object):
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


def mock_response_get_doctor(
    code: Optional[int] = None,
    cookies: Optional[str] = None,
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
    body = {
        "name": "".join(
            random.choice(string.ascii_uppercase + string.digits) for _ in range(8)
        ),
        "practice_location": "".join(
            random.choice(string.ascii_uppercase) for _ in range(8)
        ),
        "doctor_md": "".join(random.choice(string.digits) for _ in range(10)),
    }

    return _non_null_options_to_dict(
        _Option("statusCode", code),
        _Option("reasonPhrase", reason),
        _Option("body", body),
        _Option("cookies", cookies),
    )


def mock_response_post_is_physician_recommended(
    code: Optional[int] = None,
    cookies: Optional[str] = None,
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
    body = {"is_recommended": "true"}

    return _non_null_options_to_dict(
        _Option("statusCode", code),
        _Option("reasonPhrase", reason),
        _Option("body", body),
        _Option("cookies", cookies),
    )


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


def _to_time(value: Union[_Time, int]) -> _Time:
    if not isinstance(value, _Time):
        value = seconds(value)
    return value


def _to_time_to_live(time: Union[_Time, int]) -> Dict[str, Any]:
    time = _to_time(time)
    return {"timeToLive": time.value, "timeUnit": time.unit, "unlimited": False}
