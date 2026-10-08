"""
Shared sample data for the test suite.

The helpers below build JSON payloads shaped like the ones returned by the RUDI
Producer external API. They let the connectors and the reader be tested without
any access to a real RUDI node.
"""

from copy import deepcopy

import pytest

META_UUID_A = "e8b513a1-8d0e-4824-9a7d-1087fc66af9d"
META_UUID_B = "f0e4b2c6-1a3d-4f8e-9c2b-5d7e6f8a9b0c"
MEDIA_UUID_A = "9de29661-a53a-4eea-835c-b0799e181636"
MEDIA_UUID_B = "53e40e80-87a7-43b0-b1a4-30324f45e2b5"
CONTACT_UUID_A = "f275bed9-6b62-43f1-b617-a392896a617c"
CONTACT_UUID_B = "6371498a-f9df-46a5-b4e6-9dec377ada2b"
ORG_UUID_A = "fa557d8b-0892-47aa-809b-6da59081e0aa"
ORG_UUID_B = "44f5ac9d-34d6-44d0-99a9-0496654bde5c"
NODE_URL = "https://rudi-node.test"

ORG_A = {
    "organization_id": ORG_UUID_A,
    "organization_name": "Gusikowski LLC",
    "organization_address": "4974 Altenwerth Wells, Brownville",
    "collection_tag": "rudi-test",
}
ORG_B = {
    "organization_id": ORG_UUID_B,
    "organization_name": "Breitenberg - Legros",
    "organization_address": "425 Hickle Crest, Duluth",
    "collection_tag": "rudi-test",
}


def build_contact(
    contact_id: str = CONTACT_UUID_A,
    contact_name: str = "Sherri Dickinson",
    email: str = "sherri.dickinson@irisa.fr",
) -> dict:
    return {
        "contact_id": contact_id,
        "contact_name": contact_name,
        "email": email,
        "collection_tag": "rudi-test",
    }


def build_media(
    media_id: str = MEDIA_UUID_A,
    media_name: str = "Synergistic system-worthy encoding.json",
    media_type: str = "FILE",
    file_storage_status: str | None = "available",
    url: str | None = None,
) -> dict:
    media = {
        "media_type": media_type,
        "media_id": media_id,
        "media_name": media_name,
        "connector": {
            "url": url or f"https://rudi-node.test/storage/download/{media_id}",
            "interface_contract": "dwnl",
        },
        "media_dates": {
            "created": "2023-03-03T11:15:57.226+00:00",
            "updated": "2023-03-03T11:15:57.226+00:00",
        },
        "collection_tag": "rudi-test",
    }
    if media_type == "FILE":
        media.update(
            {
                "file_type": "application/json",
                "file_size": 59016,
                "checksum": {"algo": "MD5", "hash": "4c9ee0f14e835927a1bbafde0eb89fb3"},
                "file_storage_status": file_storage_status,
                "file_status_update": "2023-03-03T11:15:57.232+00:00",
            }
        )
    return media


def build_metadata(
    global_id: str = META_UUID_A,
    resource_title: str = "Synergistic system-worthy encoding",
    local_id: str | None = "local-id-a",
    producer: dict | None = None,
    publisher: dict | None = None,
    contacts: list[dict] | None = None,
    metadata_contacts: list[dict] | None = None,
    theme: str = "education",
    keywords: list[str] | None = None,
    available_formats: list[dict] | None = None,
) -> dict:
    metadata_info: dict = {
        "api_version": "1.4.3",
        "metadata_dates": {
            "created": "2023-04-12T09:39:28.666+00:00",
            "updated": "2023-04-12T09:39:28.696+00:00",
        },
    }
    if publisher is not None:
        metadata_info["metadata_provider"] = deepcopy(publisher)
    if metadata_contacts is not None:
        metadata_info["metadata_contacts"] = deepcopy(metadata_contacts)

    return {
        "global_id": global_id,
        "resource_title": resource_title,
        "local_id": local_id,
        "synopsis": [{"lang": "fr", "text": f"synopsis of {resource_title}"}],
        "summary": [{"lang": "fr", "text": f"summary of {resource_title}"}],
        "theme": theme,
        "keywords": ["RUDI", "test"] if keywords is None else keywords,
        "producer": deepcopy(producer) if producer is not None else deepcopy(ORG_A),
        "contacts": deepcopy(contacts) if contacts is not None else [build_contact()],
        "available_formats": deepcopy(available_formats) if available_formats is not None else [build_media()],
        "dataset_dates": {
            "created": "2023-04-12T02:00:38+00:00",
            "updated": "2023-04-12T02:00:38+00:00",
            "published": "2023-04-12T09:39:28.562+00:00",
        },
        "storage_status": "pending",
        "access_condition": {
            "licence": {"licence_label": "etalab-1.0", "licence_type": "STANDARD"},
            "confidentiality": {"restricted_access": False, "gdpr_sensitive": False},
        },
        "metadata_info": metadata_info,
        "resource_languages": ["fr"],
    }


def build_catalogue() -> list[dict]:
    """
    Two metadata sharing the same producer and publisher organizations, plus a
    publisher organization that is not the producer (which is what makes the
    `RudiNodeReader.organization_list` de-duplication loops interesting).
    """
    meta_a = build_metadata(
        global_id=META_UUID_A,
        resource_title="Metadata A",
        local_id="local-id-a",
        producer=ORG_A,
        publisher=ORG_B,
        metadata_contacts=[build_contact()],
        theme="education",
        keywords=["RUDI", "test"],
        available_formats=[
            build_media(media_id=MEDIA_UUID_A, file_storage_status="available"),
            build_media(media_id=MEDIA_UUID_B, media_name="service.json", media_type="SERVICE"),
        ],
    )
    meta_b = build_metadata(
        global_id=META_UUID_B,
        resource_title="Metadata B",
        local_id="local-id-b",
        producer=ORG_A,
        publisher=ORG_B,
        contacts=[build_contact(contact_id=CONTACT_UUID_B, contact_name="Wanda Torphy", email="wanda.torphy@irisa.fr")],
        metadata_contacts=[build_contact()],
        theme="transport",
        keywords=["RUDI", "transport"],
        available_formats=[build_media(media_id=MEDIA_UUID_B, file_storage_status="missing")],
    )
    return [meta_a, meta_b]


@pytest.fixture
def rudi_meta() -> dict:
    return build_metadata()


@pytest.fixture
def catalogue() -> list[dict]:
    return build_catalogue()
