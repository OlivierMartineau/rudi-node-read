"""
Offline tests for `RudiNodeReader`.

`rudi_node_read.rudi_node_reader.RudiNodeConnector` and `https_download` are
replaced, so the reader works against a canned catalogue and never touches the
network.
"""

from copy import deepcopy
from json import loads
from pathlib import Path

import pytest
from conftest import (
    MEDIA_UUID_A,
    META_UUID_A,
    NODE_URL,
    build_catalogue,
    build_media,
    build_metadata,
)

import rudi_node_read.rudi_node_reader as reader_module
from rudi_node_read.rudi_node_reader import RudiNodeReader

UNKNOWN_UUID = "00000000-0000-4000-8000-000000000000"
MEDIA_NAME_A = "Synergistic system-worthy encoding.json"


def build_reader(monkeypatch, catalogue: list[dict] | None = None) -> RudiNodeReader:
    """
    Patch `rudi_node_read.rudi_node_reader.RudiNodeConnector` with a stub that serves
    `catalogue`, then build a `RudiNodeReader` on top of it.
    """
    served_catalogue = build_catalogue() if catalogue is None else catalogue

    class FakeConnector:
        def __init__(self, server_url: str = "", headers_user_agent: str = ""):
            self.server_url = server_url
            self.headers_user_agent = headers_user_agent

        def get_metadata_count(self) -> int:
            return len(served_catalogue)

        def get_metadata_list(self) -> list[dict]:
            return deepcopy(served_catalogue)

    monkeypatch.setattr(reader_module, "RudiNodeConnector", FakeConnector)
    return RudiNodeReader(NODE_URL)


@pytest.fixture
def reader(monkeypatch) -> RudiNodeReader:
    return build_reader(monkeypatch)


def mock_download(monkeypatch, content: bytes = b"file payload") -> None:
    monkeypatch.setattr(reader_module, "https_download", lambda _url: content)


# --------------------------------------------------------------------------- caching


def test_server_url(reader):
    assert reader.server_url == NODE_URL


def test_connector_is_rebuilt_when_lost(reader):
    reader._connector = None

    assert reader.connector is not None
    assert reader.connector.server_url == NODE_URL


def test_reset_cache(reader):
    assert reader.metadata_count == 2
    assert reader.metadata_list
    assert reader.organization_list
    assert reader.contact_list

    reader._reset_cache()

    assert reader._meta_list is None
    assert reader._meta_count == 0
    assert reader._org_list is None
    assert reader._contact_list is None
    assert reader._themes is None
    assert reader._keywords is None


def test_connect_reconnects_and_clears_the_cache(reader):
    assert reader.metadata_count == 2
    assert reader.metadata_list

    reader.connect(f"{NODE_URL}/another-node", "RudiNodeReader/other")

    assert reader.server_url == f"{NODE_URL}/another-node"
    assert reader.connector.headers_user_agent == "RudiNodeReader/other"
    assert reader._meta_list is None
    assert reader._meta_count == 0


def test_metadata_count_and_list_are_cached(reader):
    assert reader.metadata_count == 2
    assert reader.metadata_count == 2
    assert reader.connector.get_metadata_count() == 2

    assert len(reader.metadata_list) == 2
    assert reader.metadata_list is reader.metadata_list


def test_metadata_count_on_an_empty_node(monkeypatch):
    empty_reader = build_reader(monkeypatch, [])

    assert empty_reader.metadata_count == 0
    assert empty_reader.metadata_list == []


# --------------------------------------------------------------------------- summaries


def test_light_node_summary_title(reader):
    title = reader.light_node_summary_title

    assert NODE_URL in title
    assert "metadata count" in title
    assert "2" in title


def test_catalogue_summary(reader):
    summary = reader.catalogue_summary

    assert "Metadata A" in summary
    assert "Metadata B" in summary


def test_create_textual_description_single_metadata_from_a_uuid(reader):
    description = reader.create_textual_description_single_metadata(META_UUID_A)

    assert "Metadata A" in description
    assert META_UUID_A in description


def test_create_textual_description_single_metadata_from_a_metadata(reader):
    description = reader.create_textual_description_single_metadata(build_metadata(resource_title="Solo title"))

    assert "Solo title" in description


def test_create_textual_description_single_metadata_with_an_unknown_uuid(reader):
    with pytest.raises(Exception, match="No metadata with uuid"):
        reader.create_textual_description_single_metadata(UNKNOWN_UUID)


def test_create_textual_description_metadata(reader):
    from_uuid = reader.create_textual_description_metadata(META_UUID_A)
    from_metadata = reader.create_textual_description_metadata(build_metadata())

    assert "Metadata A" in from_uuid
    assert "Solo title" not in from_metadata

    from_list = reader.create_textual_description_metadata(reader.metadata_list)
    assert "Metadata A" in from_list and "Metadata B" in from_list

    from_list_with_summary = reader.create_textual_description_metadata(reader.metadata_list, show_node_summary=True)
    assert NODE_URL in from_list_with_summary


# --------------------------------------------------------------------------- searching


def test_find_metadata_with_source_id(reader):
    assert reader.find_metadata_with_source_id("local-id-a")["global_id"] == META_UUID_A
    assert reader.find_metadata_with_source_id("no-such-local-id") is None


def test_find_metadata_with_media_uuid(reader):
    assert reader.find_metadata_with_media_uuid(MEDIA_UUID_A)["global_id"] == META_UUID_A
    assert reader.find_metadata_with_media_uuid(UNKNOWN_UUID) is None


def test_organization_list_dedupes_producer_and_publisher(reader):
    organization_ids = [org["organization_id"] for org in reader.organization_list]

    assert len(organization_ids) == 2
    assert len(set(organization_ids)) == 2
    assert reader.organization_names == sorted(reader.organization_names)
    assert reader.organization_names == ["Breitenberg - Legros", "Gusikowski LLC"]


def test_contact_list_merges_metadata_and_publisher_contacts(reader):
    contact_ids = [contact["contact_id"] for contact in reader.contact_list]

    assert len(contact_ids) == 2
    assert len(set(contact_ids)) == 2
    assert reader.contact_names == sorted(reader.contact_names)


# --------------------------------------------------------------------------- downloads


def test_download_media_from_info_skips_services():
    result = RudiNodeReader._download_media_from_info(build_media(media_type="SERVICE"), "/tmp")

    assert result["status"] == "skipped"
    assert result["media"]["media_type"] == "SERVICE"


def test_download_media_from_info_reports_missing_files():
    result = RudiNodeReader._download_media_from_info(build_media(file_storage_status="missing"), "/tmp")

    assert result["status"] == "missing"
    assert result["media"]["file_storage_status"] == "missing"


def test_download_media_from_info_requires_an_existing_folder(tmp_path):
    with pytest.raises(FileNotFoundError, match="does not exist"):
        RudiNodeReader._download_media_from_info(build_media(), str(tmp_path / "nowhere"))


def test_download_media_from_info_downloads_the_file(monkeypatch, tmp_path):
    mock_download(monkeypatch, b"some bytes")

    result = RudiNodeReader._download_media_from_info(build_media(), str(tmp_path))

    assert result["status"] == "downloaded"
    assert result["media"]["media_id"] == MEDIA_UUID_A
    assert result["media"]["media_name"] == MEDIA_NAME_A
    assert result["media"]["created"] is not None
    assert result["media"]["updated"] is not None
    assert Path(result["media"]["file_path"]).read_bytes() == b"some bytes"


def test_download_file_with_uuid(reader, monkeypatch, tmp_path):
    mock_download(monkeypatch)

    result = reader.download_file_with_uuid(MEDIA_UUID_A, str(tmp_path))

    assert result["status"] == "downloaded"
    assert reader.download_file_with_uuid(UNKNOWN_UUID, str(tmp_path)) is None


def test_download_file_with_name(reader, monkeypatch, tmp_path):
    mock_download(monkeypatch)

    result = reader.download_file_with_name(MEDIA_NAME_A, str(tmp_path))

    assert result["status"] == "downloaded"
    assert reader.download_file_with_name("no-such-file.json", str(tmp_path)) is None


def test_download_files_for_metadata(reader, monkeypatch, tmp_path):
    mock_download(monkeypatch)

    result = reader.download_files_for_metadata(META_UUID_A, str(tmp_path))

    assert len(result["downloaded"]) == 1
    assert len(result["skipped"]) == 1
    assert result["missing"] == []


def test_download_files_for_metadata_requires_an_existing_folder(reader, tmp_path):
    with pytest.raises(FileNotFoundError, match="does not exist"):
        reader.download_files_for_metadata(META_UUID_A, str(tmp_path / "nowhere"))


def test_download_files_for_metadata_without_any_media(monkeypatch, tmp_path):
    reader_without_media = build_reader(monkeypatch, [build_metadata(available_formats=[])])

    assert reader_without_media.download_files_for_metadata(META_UUID_A, str(tmp_path)) is None


# --------------------------------------------------------------------------- persistence


def test_save_metadata_to_file(reader, tmp_path):
    reader.save_metadata_to_file(str(tmp_path))

    saved = loads((tmp_path / "rudi_node_metadata.json").read_text(encoding="utf-8"))

    assert len(saved) == 2
    assert saved[0]["global_id"] == META_UUID_A


def test_save_metadata_to_file_with_a_custom_name(reader, tmp_path):
    reader.save_metadata_to_file(str(tmp_path), "subset.json")

    assert (tmp_path / "subset.json").is_file()
