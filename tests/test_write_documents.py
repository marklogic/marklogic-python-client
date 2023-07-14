import pytest

from marklogic import Client
from marklogic.documents import Document

DEFAULT_PERMS = {"python-tester": ["read", "update"]}


def test_write_json(client: Client):
    # Verifies that JSON can be either a dict or a string.
    response = client.documents.write(
        [
            Document("/temp/doc1.json", {"doc": 1}, permissions=DEFAULT_PERMS),
            Document("/temp/doc2.json", '{"doc": 2}', permissions=DEFAULT_PERMS),
        ]
    )

    assert 200 == response.status_code
    assert response.headers["Content-type"].startswith("application/json")
    data = response.json()
    assert len(data["documents"]) == 2

    doc1 = client.get("v1/documents?uri=/temp/doc1.json").json()
    assert 1 == doc1["doc"]
    doc2 = client.get("v1/documents?uri=/temp/doc2.json").json()
    assert 2 == doc2["doc"]


def test_return_xml(client: Client):
    """
    Verifies that the headers passed in by a user aren't lost when the client sets
    the Content-type to multipart/mixed.
    """
    docs = [
        Document("/temp/doc1.json", {"doc": 1}, permissions=DEFAULT_PERMS),
        Document("/temp/doc2.json", {"doc": 2}, permissions=DEFAULT_PERMS),
    ]
    response = client.documents.write(docs, headers={"Accept": "application/xml"})

    assert response.headers["Content-type"].startswith("application/xml")
    assert response.text.startswith("<rapi:documents")


def test_write_json_and_xml(client: Client):
    response = client.documents.write(
        [
            Document("/temp/doc1.json", {"doc": 1}, permissions=DEFAULT_PERMS),
            Document("/temp/doc2.xml", "<doc>2</doc>", permissions=DEFAULT_PERMS),
        ]
    )
    assert 200 == response.status_code

    doc1 = client.get("v1/documents?uri=/temp/doc1.json").json()
    assert 1 == doc1["doc"]
    doc2_text = client.get("v1/documents?uri=/temp/doc2.xml").text
    assert doc2_text.__contains__("<doc>2</doc>")


def test_content_types(client: Client):
    """
    Verifies a user can specify a content type for each document where MarkLogic is not
    able to determine a type based on the URI.
    """
    response = client.documents.write(
        [
            Document(
                "/temp/doc1",
                {"doc": 1},
                content_type="application/json",
                permissions=DEFAULT_PERMS,
            ),
            Document(
                "/temp/doc2",
                "<doc>2</doc>",
                content_type="application/xml",
                permissions=DEFAULT_PERMS,
            ),
        ]
    )
    assert 200 == response.status_code

    doc1 = client.get("v1/documents?uri=/temp/doc1").json()
    assert 1 == doc1["doc"]
    doc2_text = client.get("v1/documents?uri=/temp/doc2").text
    assert doc2_text.__contains__("<doc>2</doc>")


def test_single_doc(client):
    response = client.documents.write(
        [Document("/temp/doc1.json", {"doc": 1}, permissions=DEFAULT_PERMS)]
    )
    assert 200 == response.status_code

    doc1 = client.get("v1/documents?uri=/temp/doc1.json").json()
    assert 1 == doc1["doc"]


@pytest.mark.skip("Will get this working when supporting batch-level metadata")
def test_server_generated_uri(client):
    response = client.documents.write(
        [
            Document(
                None,
                {"doc": "serveruri"},
                extension=".json",
                directory="/temp/",
                permissions=DEFAULT_PERMS,
            )
        ]
    )
    assert 200 == response.status_code

    # Do a search to find the URI.
    data = client.get("/v1/search?q=serveruri&format=json").json()
    assert 1 == data["total"]
    uri = data["results"][0]["uri"]

    doc1 = client.get(f"v1/documents?uri={uri}").json()
    assert "serveruri" == doc1["doc"]


def test_repair_xml(client):
    response = client.documents.write(
        [
            Document(
                "/temp/doc1.xml",
                "<doc>needs <b>closing tag</doc>",
                repair="full",
                permissions=DEFAULT_PERMS,
            )
        ]
    )
    assert 200 == response.status_code

    xml = client.get("v1/documents?uri=/temp/doc1.xml").text
    assert xml.__contains__("<doc>needs <b>closing tag</b></doc>")


@pytest.mark.skip("Will succeed only if MarkLogic converters are installed.")
def test_extract_binary(client):
    content = "MarkLogic and Python".encode("ascii")
    response = client.documents.write(
        [
            Document(
                "/temp/doc1.bin",
                content,
                extract="properties",
                permissions=DEFAULT_PERMS,
            )
        ]
    )
    assert 200 == response.status_code


def test_optimistic_locking(client):
    response = client.documents.write(
        [
            Document(
                "/temp/doc1.json", {"content": "original"}, permissions=DEFAULT_PERMS
            )
        ]
    )
    assert 200 == response.status_code

    # The ETag defines the version of the document.
    etag = client.get("v1/documents?uri=/temp/doc1.json").headers["ETag"]

    # Update the document, passing in the current version_id based on the ETag.
    response = client.documents.write(
        [
            Document(
                "/temp/doc1.json",
                {"content": "updated!"},
                version_id=etag,
                permissions=DEFAULT_PERMS,
            )
        ]
    )
    assert 200 == response.status_code

    # Verify the doc was updated.
    doc = client.get("v1/documents?uri=/temp/doc1.json").json()
    assert "updated!" == doc["content"]

    # Next update should fail since the ETag is no longer the current version.
    response = client.documents.write(
        [
            Document(
                "/temp/doc1.json",
                {"this": "should fail"},
                version_id=etag,
                permissions=DEFAULT_PERMS,
            )
        ]
    )
    assert 412 == response.status_code, "412 is returned when the versionId is invalid."
    assert response.text.__contains__("RESTAPI-CONTENTWRONGVERSION")


def test_temporal_doc(client):
    content = {
        "text": "hello world",
        "systemStart": "2014-04-03T11:00:00",
        "systemEnd": "2014-04-03T16:00:00",
        "validStart": "2014-04-03T11:00:00",
        "validEnd": "2014-04-03T16:00:00",
    }

    response = client.documents.write(
        [
            Document(
                "/temp/doc1.json",
                content,
                temporal_document="custom1",
                permissions=DEFAULT_PERMS,
            )
        ],
        params={"temporal-collection": "temporal-collection"},
    )
    assert 200 == response.status_code

    # Verify that the temporal doc was written to the "custom1" collection. This will be
    # easier to do once we have support for reading documents and their metadata.
    data = client.get("/v1/search?collection=custom1&format=json").json()
    assert 1 == data["total"]
    assert "/temp/doc1.json" == data["results"][0]["uri"]


def test_metadata_no_content(client: Client):
    print("TODO!")
