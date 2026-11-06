# Copyright (c) 2023-2026 Progress Software Corporation and/or its subsidiaries or affiliates. All Rights Reserved.


import pytest
from urllib3.filepost import encode_multipart_formdata

from marklogic import Client
from marklogic.documents import Document

DEFAULT_PERMS = {"python-tester": ["read", "update"]}


def _render(doc: Document) -> str:
    fields = [f for f in (doc.to_metadata_request_field(), doc.to_request_field()) if f]
    body, _ = encode_multipart_formdata(fields, boundary="BOUNDARY")
    return body.decode("utf-8")


def _part_headers(body: str) -> list[str]:
    parts = body.split("--BOUNDARY")[1:-1]
    return [part.split("\r\n\r\n", 1)[0] for part in parts]


@pytest.mark.parametrize(
    "uri",
    [
        "/a.json\r\nX-Injected: 1",
        "/a.json\r\n\r\ninjected body",
        "/a.json\nX-Injected: 1",
        "/a.json\x00",
    ],
)
def test_uri_with_control_chars_is_rejected(uri):
    with_metadata = Document(uri, {"a": 1}, permissions=DEFAULT_PERMS)
    with pytest.raises(ValueError):
        with_metadata.to_metadata_request_field()
    with pytest.raises(ValueError):
        with_metadata.to_request_field()


@pytest.mark.parametrize(
    "kwargs",
    [
        {"extract": "properties\r\nX-Evil: y"},
        {"extract": "properties;versionId=1"},
        {"version_id": "1;temporal-document=/x.json"},
        {"version_id": "1\r\nX-Evil: y"},
        {"version_id": '"1";extract=properties'},
        {"version_id": '"1'},
        {"version_id": '"123\\"'},
        {"temporal_document": "/x.json;category=metadata"},
        {"temporal_document": '/x.json"'},
    ],
)
def test_unsafe_disposition_params_are_rejected(kwargs):
    doc = Document("/a.json", {"a": 1}, **kwargs)
    with pytest.raises(ValueError):
        doc.to_request_field()


@pytest.mark.parametrize(
    "kwargs",
    [
        {"extension": ".json;category=metadata"},
        {"extension": ".json\r\nX-Evil: y"},
        {"directory": "/temp/;versionId=1"},
        {"directory": "/temp/\r\n\r\nbody"},
    ],
)
def test_unsafe_server_generated_uri_params_are_rejected(kwargs):
    doc = Document(None, {"a": 1}, **kwargs)
    with pytest.raises(ValueError):
        doc.to_request_field()


@pytest.mark.parametrize(
    "repair", ["partial", "full;extract=properties", "full\r\nX-Evil: y"]
)
def test_invalid_repair_is_rejected(repair):
    doc = Document("/a.xml", "<a/>", repair=repair)
    with pytest.raises(ValueError):
        doc.to_request_field()


def test_metadata_part_does_not_contain_raw_uri():
    uri = '/doc;category=content;versionId=1 "x".json'
    body = _render(Document(uri, {"a": 1}, permissions=DEFAULT_PERMS))
    metadata_headers, content_headers = _part_headers(body)

    assert metadata_headers.count("\r\n") == 2, "Expected only two header lines"
    assert "filename=/doc" not in metadata_headers
    assert 'filename="/doc;category=content;versionId=1 %22x%22.json"' in (
        metadata_headers
    )
    assert "category=metadata" in metadata_headers
    assert "category=content" not in metadata_headers.split('"')[0]
    assert content_headers.count("\r\n") == 1


def test_valid_params_are_rendered():
    body = _render(
        Document(
            "/a.xml",
            "<a/>",
            repair="full",
            extract="properties",
            version_id='"12345"',
            temporal_document="/logical/a.xml",
        )
    )
    (content_headers,) = _part_headers(body)
    assert (
        "Content-Disposition: attachment;repair=full;extract=properties;"
        'versionId="12345";temporal-document=/logical/a.xml;'
    ) in content_headers
    assert content_headers.count("\r\n") == 1

    body = _render(Document(None, {"a": 1}, extension=".json", directory="/temp/"))
    assert "inline;extension=.json;directory=/temp/;" in body


def test_write_uri_with_semicolon_and_metadata(client: Client):
    uri = "/temp/doc;copy.json"
    response = client.documents.write(
        Document(uri, {"doc": 1}, permissions=DEFAULT_PERMS, collections=["c1"])
    )
    assert 200 == response.status_code

    docs = client.documents.read(uri, categories=["content", "metadata"])
    assert len(docs) == 1
    doc = docs[0]
    assert uri == doc.uri
    assert {"doc": 1} == doc.content
    assert ["c1"] == doc.collections
    assert ["read", "update"] == sorted(doc.permissions["python-tester"])


def test_write_with_unquoted_version_id(client: Client):
    uri = "/temp/doc1.json"
    response = client.documents.write(
        Document(uri, {"content": "original"}, permissions=DEFAULT_PERMS)
    )
    assert 200 == response.status_code

    etag = client.get(f"v1/documents?uri={uri}").headers["ETag"]
    response = client.documents.write(
        Document(
            uri,
            {"content": "updated"},
            version_id=etag.strip('"'),
            permissions=DEFAULT_PERMS,
        )
    )
    assert 200 == response.status_code
    assert "updated" == client.get(f"v1/documents?uri={uri}").json()["content"]
