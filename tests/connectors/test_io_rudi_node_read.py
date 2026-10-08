"""
Offline tests for `RudiNodeConnector`.

`RudiNodeConnector.request` is replaced by a `RequestRecorder`, which records
every outgoing request and answers it from an in-process script, so no RUDI node
is ever contacted.
"""

from copy import deepcopy

import pytest
from conftest import (
    MEDIA_UUID_A,
    MEDIA_UUID_B,
    META_UUID_A,
    META_UUID_B,
    NODE_URL,
    build_catalogue,
    build_media,
    build_metadata,
)

from rudi_node_read.connectors.io_connector import REDIRECTION, STATUS
from rudi_node_read.connectors.io_rudi_node_read import RudiNodeConnector
from rudi_node_read.rudi_types.rudi_meta import RudiMetadata

REDIRECTED_HASH_URL = f"{NODE_URL}/api/admin/hash"


class RequestRecorder:
    """Stands in for `RudiNodeConnector.request`: records the call, then answers with `handler(url)`."""

    def __init__(self, handler=None):
        self.calls: list[dict] = []
        self.handler = handler or (lambda _url: {"total": 0})

    def __call__(self, url, req_method="GET", headers=None, **_kwargs):
        self.calls.append({"url": url, "req_method": req_method, "headers": headers})
        result = self.handler(url)
        if isinstance(result, Exception):
            raise result
        return result

    @property
    def last_url(self) -> str:
        return self.calls[-1]["url"]


@pytest.fixture
def recorder() -> RequestRecorder:
    return RequestRecorder()


@pytest.fixture
def connector(recorder, monkeypatch) -> RudiNodeConnector:
    monkeypatch.setattr(RudiNodeConnector, "request", recorder)
    return RudiNodeConnector(NODE_URL)


def test_constructor_checks_the_node_connection(connector, recorder):
    assert connector._prefix == "catalog"
    assert connector._headers == {
        "User-Agent": "RudiNodeConnector",
        "Content-type": "text/plain",
        "Accept": "application/json",
    }
    assert recorder.calls[0]["url"] == "catalog/admin/hash"
    assert recorder.calls[0]["headers"]["User-Agent"] == "RudiNodeConnector"


def test_constructor_uses_the_custom_user_agent(recorder, monkeypatch):
    monkeypatch.setattr(RudiNodeConnector, "request", recorder)
    RudiNodeConnector(NODE_URL, headers_user_agent="RudiNodeReader/test")
    assert recorder.calls[0]["headers"]["User-Agent"] == "RudiNodeReader/test"


def test_constructor_fails_when_the_node_does_not_answer(monkeypatch):
    recorder = RequestRecorder(handler=lambda _url: None)
    monkeypatch.setattr(RudiNodeConnector, "request", recorder)
    with pytest.raises(ConnectionError, match="Connection failed"):
        RudiNodeConnector(NODE_URL)


def test_get_catalog_falls_back_to_the_api_prefix(connector, recorder):
    answers = iter([ConnectionError("boom"), {"hash": "abc"}])
    recorder.handler = lambda _url: next(answers)

    assert connector._get_catalog("admin/hash") == {"hash": "abc"}
    assert connector._prefix == "api"
    assert recorder.last_url == "api/admin/hash"


def test_get_catalog_follows_a_redirection(connector, recorder):
    answers = iter([{STATUS: 301, REDIRECTION: REDIRECTED_HASH_URL}, {"hash": "abc"}])
    recorder.handler = lambda _url: next(answers)

    assert connector._get_catalog("admin/hash") == {"hash": "abc"}
    assert connector._prefix == f"{NODE_URL}/api"
    assert recorder.last_url == REDIRECTED_HASH_URL


def test_get_catalog_rejects_a_redirection_to_another_url(connector, recorder):
    recorder.handler = lambda _url: {STATUS: 302, REDIRECTION: "https://elsewhere.test/some/other/url"}

    with pytest.raises(ConnectionError, match="Connection failed"):
        connector._get_catalog("admin/hash")


def test_get_catalog_fails_when_the_redirection_does_not_answer(connector, recorder):
    answers = iter([{STATUS: 302, REDIRECTION: REDIRECTED_HASH_URL}, None])
    recorder.handler = lambda _url: next(answers)

    with pytest.raises(ConnectionError, match="Connection failed"):
        connector._get_catalog("admin/hash")


def test_get_metadata_with_uuid(connector, recorder):
    recorder.handler = lambda _url: build_metadata()

    assert connector.get_metadata_with_uuid(META_UUID_A)["global_id"] == META_UUID_A
    assert recorder.last_url == f"catalog/v1/resources/{META_UUID_A}"


def test_get_metadata_with_filter(connector, recorder):
    recorder.handler = lambda _url: [build_metadata(), build_metadata(global_id=META_UUID_B)]

    res = connector.get_metadata_with_filter({"theme": "education", "keywords": "RUDI"})

    assert len(res) == 2
    assert recorder.last_url == "catalog/v1/resources?theme=education&keywords=RUDI"


def test_get_metadata_count_requires_a_dict(connector, recorder):
    recorder.handler = lambda _url: "not a dict"

    with pytest.raises(TypeError, match="dict"):
        connector.get_metadata_count()


def test_get_metadata_ids(connector, recorder):
    recorder.handler = lambda _url: {"items": [{"global_id": META_UUID_A}]}

    assert connector.get_metadata_ids() == [{"global_id": META_UUID_A}]
    assert recorder.last_url == "catalog/v1/resources?fields=global_id,resource_title"


def test_get_list_media_for_metadata(connector, recorder):
    recorder.handler = lambda _url: build_metadata(
        available_formats=[
            build_media(media_id=MEDIA_UUID_A),
            build_media(media_id=MEDIA_UUID_B, media_name="service.json", media_type="SERVICE"),
        ]
    )

    assert connector.get_list_media_for_metadata(META_UUID_A) == [
        {
            "url": f"{NODE_URL}/storage/download/{MEDIA_UUID_A}",
            "type": "FILE",
            "meta_contact": MEDIA_UUID_A,
            "id": MEDIA_UUID_A,
        },
        {
            "url": f"{NODE_URL}/storage/download/{MEDIA_UUID_B}",
            "type": "SERVICE",
            "meta_contact": MEDIA_UUID_B,
            "id": MEDIA_UUID_B,
        },
    ]


def test_get_list_media_for_metadata_requires_a_dict(connector, recorder):
    recorder.handler = lambda _url: "not a metadata"

    with pytest.raises(TypeError, match="dict"):
        connector.get_list_media_for_metadata(META_UUID_A)


def test_get_list_media_for_metadata_requires_a_media_list(connector, recorder):
    recorder.handler = lambda _url: {"available_formats": "not a list"}

    with pytest.raises(TypeError, match="list"):
        connector.get_list_media_for_metadata(META_UUID_A)


def test_get_rudi_meta_with_uuid(connector, recorder):
    recorder.handler = lambda _url: build_metadata()
    assert isinstance(connector.get_rudi_meta_with_uuid(META_UUID_A), RudiMetadata)

    recorder.handler = lambda _url: "not a metadata"
    assert connector.get_rudi_meta_with_uuid(META_UUID_A) is None


def test_get_rudi_meta_with_filter(connector, recorder):
    recorder.handler = lambda _url: [build_metadata(), build_metadata(global_id=META_UUID_B)]
    res = connector.get_rudi_meta_with_filter({"theme": "education"})
    assert len(res) == 2
    assert all(isinstance(meta, RudiMetadata) for meta in res)

    recorder.handler = lambda _url: []
    assert connector.get_rudi_meta_with_filter({"theme": "education"}) == []

    recorder.handler = lambda _url: {"total": 0}
    assert connector.get_rudi_meta_with_filter({"theme": "education"}) == []


def test_get_rudi_meta_list(connector, recorder):
    catalogue = build_catalogue()

    def handler(url: str):
        if "resources?limit=1" in url:
            return {"total": len(catalogue)}
        return {"total": len(catalogue), "items": deepcopy(catalogue)}

    recorder.handler = handler
    res = connector.get_rudi_meta_list()

    assert len(res) == 2
    assert all(isinstance(meta, RudiMetadata) for meta in res)
    assert recorder.last_url.endswith("limit=2&offset=0")


def test_get_rudi_meta_list_when_the_node_is_empty(connector, recorder):
    recorder.handler = lambda _url: {"total": 0}

    assert connector.get_rudi_meta_list() == []
