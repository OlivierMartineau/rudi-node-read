
import pytest

from rudi_node_read.utils.err import (
    HttpError,
    IniMissingValueException,
    IniUnexpectedValueException,
    LiteralUnexpectedValueException,
    MissingEnvironmentVariableException,
    UnexpectedValueException,
    rudi_api_http_error_to_string,
)


def test_MissingEnvironmentVariableException():
    err = MissingEnvironmentVariableException("ENV_VAR", "for testing")
    target_err_msg = "an environment variable should be defined for testing: ENV_VAR"
    assert str(err) == target_err_msg
    try:
        raise err
    except MissingEnvironmentVariableException as e:
        assert str(e) == target_err_msg


def test_IniMissingValueException():
    err = IniMissingValueException("SECTION", "SUBSECTION", "testing")
    target_err_msg = "Missing value in INI config file for parameter SECTION.SUBSECTION: testing"
    assert str(err) == target_err_msg
    try:
        raise err
    except IniMissingValueException as e:
        assert str(e) == target_err_msg


def test_IniUnexpectedValueException():
    err = IniUnexpectedValueException("SECTION", "SUBSECTION", "testing")
    target_err_msg = "Unexpected value in INI config file for parameter SECTION.SUBSECTION: testing"
    assert str(err) == target_err_msg
    try:
        raise err
    except IniUnexpectedValueException as e:
        assert str(e) == target_err_msg


def test_UnexpectedValueException():
    err = UnexpectedValueException("param", "val1", "val2")
    target_err_msg = "Unexpected value for parameter 'param': expected 'val1', got 'val2'"
    assert str(err) == target_err_msg
    try:
        raise err
    except UnexpectedValueException as e:
        assert str(e) == target_err_msg


def test_ULiteralUnexpectedValueException():
    err = LiteralUnexpectedValueException("val", ("valA", "valB"), "error")
    target_err_msg = "error. Expected ('valA', 'valB'), got 'val'"
    assert str(err) == target_err_msg
    try:
        raise err
    except LiteralUnexpectedValueException as e:
        assert str(e) == target_err_msg


def test_rudi_api_http_error_to_string():
    assert rudi_api_http_error_to_string(444, "TestError", "testing err msg") == "ERR 444 TestError: testing err msg"


def test_HttpError():
    err = HttpError("something went wrong")
    assert str(err) == "HTTP ERR something went wrong"


def test_HttpError_with_request_context():
    err = HttpError("boom", req_method="GET", base_url="https://node.test/api", url="v1/resources")
    assert str(err) == "HTTP ERR for request 'GET https://node.test/api/v1/resources' -> boom"


def test_HttpError_from_a_dict_with_a_status():
    err = HttpError({"status": 500, "error": "InternalServerError", "message": "boom"})
    assert str(err) == "HTTP ERR ERR 500 InternalServerError: boom"


def test_HttpError_from_a_dict_with_a_status_code():
    err = HttpError({"statusCode": 404, "error": "NotFound", "message": "no such resource"})
    assert str(err) == "HTTP ERR ERR 404 NotFound: no such resource"


def test_HttpError_from_a_dict_with_request_context():
    err = HttpError(
        {"status": 500, "error": "Boom", "message": "kaboom"},
        req_method="GET",
        base_url="https://node.test/api",
        url="v1/resources",
    )
    assert str(err) == "HTTP ERR for request 'GET https://node.test/api/v1/resources' -> ERR 500 Boom: kaboom"


def test_HttpError_from_a_dict_without_a_status():
    # `error` and `message` are there, but neither `status` nor `statusCode`: the payload is inlined as-is
    err = HttpError({"error": "NotFound", "message": "no such resource"})
    assert str(err) == "HTTP ERR {'error': 'NotFound', 'message': 'no such resource'}"


def test_HttpError_from_a_dict_without_an_error_message():
    # not shaped like a RUDI API error: the payload is stringified
    err = HttpError({"detail": "boom"})
    assert str(err) == "HTTP ERR {'detail': 'boom'}"


def test_HttpError_is_raised():
    with pytest.raises(HttpError, match="Connection refused"):
        raise HttpError("Connection refused", req_method="GET", base_url="https://node.test")
