from json import dumps

import pytest

from rudi_node_read.connectors import io_connector
from rudi_node_read.connectors.io_connector import (
    REDIRECTION,
    STATUS,
    Connector,
    https_download,
)
from rudi_node_read.utils.err import HttpError, LiteralUnexpectedValueException

URL_NOT_FOUND = "https://node.test/storage/download/missing"
URL_FOUND = "https://node.test/storage/download/9de29661-a53a-4eea-835c-b0799e181636"


class FakeResponse:
    def __init__(self, status: int = 200, body: bytes = b"{}", headers: dict | None = None):
        self.status = status
        self._body = body
        self._headers = headers or {}

    def read(self) -> bytes:
        return self._body

    def getheader(self, name: str):
        return self._headers.get(name)


class FakeConnection:
    def __init__(self, response: FakeResponse | None = None, error: Exception | None = None):
        self.response = response or FakeResponse()
        self.error = error
        self.requests: list[dict] = []
        self.closed = False

    def request(self, method, url, body=None, headers=None):
        self.requests.append({"method": method, "url": url, "body": body, "headers": headers})
        if self.error is not None:
            raise self.error

    def getresponse(self) -> FakeResponse:
        return self.response

    def close(self):
        self.closed = True


@pytest.fixture
def connection(monkeypatch) -> FakeConnection:
    fake = FakeConnection()
    monkeypatch.setattr(io_connector, "HTTPConnection", lambda _host: fake)
    monkeypatch.setattr(io_connector, "HTTPSConnection", lambda _host: fake)
    return fake


@pytest.fixture
def connector() -> Connector:
    return Connector("http://node.test/api")


def test_https_download_only_supports_https():
    with pytest.raises(NotImplementedError, match="only HTTPS"):
        https_download("http://node.test/some/file")


def test_https_download_success(connection):
    connection.response = FakeResponse(200, b"file content")
    assert https_download(URL_FOUND, should_show_debug_line=True) == b"file content"
    assert connection.requests[0] == {"method": "GET", "url": URL_FOUND, "body": None, "headers": None}
    assert connection.closed


def test_https_download_failure(connection):
    connection.response = FakeResponse(404, b"")
    assert https_download(URL_NOT_FOUND) is None
    assert not connection.closed


def test_connector_init():
    a_connector = Connector("http://node.test/api")
    assert a_connector.scheme == "http"
    assert a_connector.host == "node.test"
    assert a_connector.path == "/api"
    assert a_connector.base_url == "http://node.test/api"
    assert a_connector.full_url("v1/resources") == "http://node.test/api/v1/resources"
    assert a_connector.full_path("v1/resources") == "/api/v1/resources"
    assert a_connector.full_url() == "http://node.test/api/"


def test_connector_init_rejects_unknown_scheme():
    with pytest.raises(NotImplementedError, match="only http and https"):
        Connector("ftp://node.test/api")


def test_connector_from_json():
    with pytest.raises(NotImplementedError):
        Connector("http://node.test/api").from_json()


def test_request_rejects_an_unknown_method(connector, connection):
    with pytest.raises(LiteralUnexpectedValueException, match="incorrect type for request method"):
        connector.request(url="/v1/resources", req_method="PATCH")


def test_request_uses_default_headers(connector, connection):
    connection.response = FakeResponse(200, b"OK")
    assert connector.request(url="/v1/resources") == "OK"
    assert connection.requests[0]["method"] == "GET"
    assert connection.requests[0]["url"] == "/api/v1/resources"
    assert connection.requests[0]["headers"] == {"Content-Type": "text/plain", "Accept": "application/json"}


def test_request_serializes_a_dict_body(connector, connection):
    connection.response = FakeResponse(200, b'{"result": "created"}')
    res = connector.request(url="/v1/resources", req_method="POST", body={"title": "A"}, headers={"X-Test": "1"})
    assert res == {"result": "created"}
    sent = connection.requests[0]
    assert sent["method"] == "POST"
    assert sent["headers"]["Content-type"] == "application/json"
    assert sent["headers"]["X-Test"] == "1"
    assert sent["body"] == dumps({"title": "A"})


def test_request_rethrows_connection_errors(connector, connection):
    connection.error = ConnectionRefusedError(111, "Connection refused")
    with pytest.raises(ConnectionRefusedError):
        connector.request(url="/v1/resources")


def test_parse_response_returns_the_redirection(connector, connection):
    connection.response = FakeResponse(302, headers={"location": "https://other.test/api/v1/resources"})
    res = connector.parse_response(connection, "/v1/resources", "GET", {})
    assert res == {STATUS: 302, REDIRECTION: "https://other.test/api/v1/resources"}


def test_parse_response_ignores_an_unexpected_status(connector, connection):
    connection.response = FakeResponse(204, b"")
    assert connector.parse_response(connection, "/v1/resources", "GET", {}) is None


def test_parse_response_raises_on_an_error_status(connector, connection):
    connection.response = FakeResponse(500, b'{"error": "boom"}')
    with pytest.raises(HttpError, match="HTTP ERR"):
        connector.parse_response(connection, "/v1/resources", "GET", {})


def test_parse_response_returns_a_json_body(connector, connection):
    connection.response = FakeResponse(200, b'["a", "b"]')
    assert connector.parse_response(connection, "/v1/resources", "GET", {}) == ["a", "b"]


def test_parse_response_returns_a_text_body(connector, connection):
    connection.response = FakeResponse(200, b"plain text")
    assert connector.parse_response(connection, "/v1/resources", "GET", {}) == "plain text"
