from hashlib import md5, sha256, sha512
from pathlib import Path
from types import SimpleNamespace

import pytest

from rudi_node_read.utils import file_utils
from rudi_node_read.utils.file_utils import (
    FileDetails,
    check_is_dir,
    check_is_file,
    exists_file,
    get_file_charset,
    get_file_extension,
    get_file_hash,
    get_file_mime,
    get_file_size,
    is_dir,
    is_file,
    make_dir,
)

SAMPLE_TEXT = "hello rudi"
SAMPLE_PNG = str(Path(__file__).resolve().parents[2] / "dwnld" / "unicorn.png")


def fake_magic(monkeypatch, mime_type):
    """Replace `puremagic.magic_file` so that the MIME branches can be tested deterministically."""
    monkeypatch.setattr(file_utils, "magic_file", lambda _path: [SimpleNamespace(mime_type=mime_type)])


def test_is_dir(tmp_path):
    assert is_dir(str(tmp_path))
    assert not is_dir(str(tmp_path / "does-not-exist"))


def test_check_is_dir(tmp_path):
    assert check_is_dir(str(tmp_path)) == str(tmp_path)
    with pytest.raises(FileNotFoundError):
        check_is_dir(str(tmp_path / "does-not-exist"))
    with pytest.raises(FileNotFoundError, match="not a directory"):
        check_is_dir(str(tmp_path / "does-not-exist"), "not a directory")


def test_make_dir(tmp_path):
    new_dir = tmp_path / "made-by-test"
    assert make_dir(str(new_dir)) == str(new_dir)
    assert is_dir(str(new_dir))
    # Second call goes through the "already exists" branch
    assert make_dir(str(new_dir)) == str(new_dir)


def test_exists_file(tmp_path):
    file_path = tmp_path / "sample.txt"
    file_path.write_text(SAMPLE_TEXT)
    assert exists_file(str(file_path))
    assert not exists_file(str(tmp_path / "other.txt"))


def test_is_file(tmp_path):
    file_path = tmp_path / "sample.txt"
    file_path.write_text(SAMPLE_TEXT)
    assert is_file(str(file_path))
    assert not is_file(str(tmp_path))


def test_check_is_file(tmp_path):
    file_path = tmp_path / "sample.txt"
    file_path.write_text(SAMPLE_TEXT)
    assert check_is_file(str(file_path)) == str(file_path)
    with pytest.raises(FileNotFoundError):
        check_is_file(str(tmp_path / "other.txt"))
    with pytest.raises(FileNotFoundError, match="not a file"):
        check_is_file(str(tmp_path), "not a file")


def test_get_file_size(tmp_path):
    file_path = tmp_path / "sample.txt"
    file_path.write_text(SAMPLE_TEXT)
    assert get_file_size(str(file_path)) == len(SAMPLE_TEXT.encode("utf-8"))


def test_get_file_extension():
    # The extension is recognized as-is
    assert get_file_extension("/somewhere/data.geojson") == ".geojson"
    # The full extension is unknown but a suffix of it is recognized
    assert get_file_extension("/somewhere/data.backup.gz") == ".gz"
    # Nothing is recognized: the raw extension is returned
    assert get_file_extension("/somewhere/data.unknown-ext") == ".unknown-ext"
    assert get_file_extension("/somewhere/no-extension") == ""


def test_get_file_mime_on_a_real_file():
    assert get_file_mime(SAMPLE_PNG) == "image/png"


def test_get_file_mime_geojson(tmp_path, monkeypatch):
    file_path = tmp_path / "areas.geojson"
    file_path.write_text("{}")
    fake_magic(monkeypatch, "application/json")
    assert get_file_mime(str(file_path)) == "application/geo+json"


def test_get_file_mime_yaml(tmp_path, monkeypatch):
    file_path = tmp_path / "data.yaml"
    file_path.write_text("a: 1")
    fake_magic(monkeypatch, "text/yaml")
    assert get_file_mime(str(file_path)) == "text/x-yaml"


def test_get_file_mime_spreadsheet(tmp_path, monkeypatch):
    file_path = tmp_path / "data.ods"
    file_path.write_text("")
    fake_magic(monkeypatch, "text/spreadsheet")
    assert get_file_mime(str(file_path)) == "application/vnd.ms-excel"


def test_get_file_mime_without_mime_type(tmp_path, monkeypatch):
    csv_path = tmp_path / "data.csv"
    csv_path.write_text("a,b\n1,2")
    txt_path = tmp_path / "data.txt"
    txt_path.write_text(SAMPLE_TEXT)

    fake_magic(monkeypatch, None)
    assert get_file_mime(str(csv_path)) == "text/csv"
    assert get_file_mime(str(txt_path)) == "application/octet-stream"


def test_get_file_charset():
    # Non-textual payloads have no charset
    assert get_file_charset(SAMPLE_PNG) is None


def test_get_file_charset_on_text(tmp_path, monkeypatch):
    file_path = tmp_path / "sample.txt"
    file_path.write_text(SAMPLE_TEXT)
    fake_magic(monkeypatch, "text/plain")
    assert get_file_charset(str(file_path)) is not None


def test_get_file_hash(tmp_path):
    file_path = tmp_path / "sample.txt"
    file_path.write_text(SAMPLE_TEXT)
    content = SAMPLE_TEXT.encode("utf-8")

    assert get_file_hash(str(file_path)) == md5(content).hexdigest()
    assert get_file_hash(str(file_path), "MD5") == md5(content).hexdigest()
    assert get_file_hash(str(file_path), "SHA-256") == sha256(content).hexdigest()
    assert get_file_hash(str(file_path), "sha256") == sha256(content).hexdigest()
    assert get_file_hash(str(file_path), "sha-512") == sha512(content).hexdigest()


def test_get_file_hash_errors(tmp_path):
    file_path = tmp_path / "sample.txt"
    file_path.write_text(SAMPLE_TEXT)
    with pytest.raises(ValueError, match="Hash algorithm"):
        get_file_hash(str(file_path), "crc32")
    with pytest.raises(ValueError, match="Hash algorithm"):
        get_file_hash(str(file_path), 42)  # type: ignore[arg-type]
    with pytest.raises(FileNotFoundError):
        get_file_hash(str(tmp_path / "other.txt"))


def test_FileDetails(tmp_path, monkeypatch):
    file_path = tmp_path / "sample.txt"
    file_path.write_text(SAMPLE_TEXT)
    fake_magic(monkeypatch, "text/plain")

    file_details = FileDetails(str(file_path))
    assert file_details.path == str(file_path)
    assert file_details.name == "sample.txt"
    assert file_details.extension == ".txt"
    assert file_details.mime == "text/plain"
    assert file_details.charset is not None
    assert file_details.size == len(SAMPLE_TEXT.encode("utf-8"))
    assert file_details.md5 == md5(SAMPLE_TEXT.encode("utf-8")).hexdigest()
    details_json = file_details.to_json()
    assert isinstance(details_json, dict)
    assert details_json["name"] == "sample.txt"
    assert FileDetails.from_json({}) is None

    with pytest.raises(FileNotFoundError):
        FileDetails(str(tmp_path / "other.txt"))


def test_FileDetails_on_a_binary_file():
    file_details = FileDetails(SAMPLE_PNG)
    assert file_details.mime == "image/png"
    assert file_details.charset is None
