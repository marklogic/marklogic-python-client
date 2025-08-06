# Copyright (c) 2023-2025 Progress Software Corporation and/or its subsidiaries or affiliates. All Rights Reserved.


from marklogic import Client
from marklogic.documents import DefaultMetadata, Document

TEST_METADATA = {
    "collections": ["c1", "c2"],
    "permissions": {
        "python-tester": ["read", "update"],
        "qconsole-user": "execute",
    },
    "quality": 1,
    "metadata_values": {"key1": "value1", "key2": "value2"},
    "properties": {
        "hello": "world",
        "xml": "<can>be embedded</can>",
        "number": 1,
    },
}


def test_all_metadata(client: Client):
    response = client.documents.write(
        Document(
            "/temp/doc1.json",
            {"content": "original"},
            *TEST_METADATA.values(),
        ),
    )
    assert 200 == response.status_code

    docs = client.documents.read("/temp/doc1.json", categories=["content", "metadata"])

    _verify_test_metadata_exists(docs[0])


def test_only_quality_and_permissions(client: Client):
    response = client.documents.write(
        Document(
            "/temp/doc1.json",
            {"doc": 1},
            permissions={
                "python-tester": ["read", "update"],
                "qconsole-user": "execute",
            },
            quality=2,
        ),
    )

    assert 200 == response.status_code

    docs = client.documents.read("/temp/doc1.json", categories=["content", "metadata"])
    assert len(docs) == 1
    doc = docs[0]
    assert 2 == doc.quality
    assert 0 == len(doc.collections)
    assert 0 == len(doc.properties.keys())
    assert 0 == len(doc.metadata_values.keys())


def test_only_quality(client: Client):
    response = client.documents.write(
        Document(
            "/temp/doc1.json",
            {"doc": 1},
            quality=2,
        ),
    )

    assert (
        500 == response.status_code
    ), "The response should be sent without permissions and thus fail because a \
        non-admin user requires at least one update permission."
    assert "XDMP-MUSTHAVEUPDATE" in response.text


def test_default_metadata(client: Client):
    """
    The REST endpoint allows for default metadata to be provided at any point in the
    multipart body, and it is expected to be applied to any document after it that does
    not have any metadata itself.
    """
    response = client.documents.write(
        [
            DefaultMetadata(*TEST_METADATA.values()),
            Document("/temp/doc1.json", {"doc": 1}),
            Document(
                "/temp/doc2.json",
                {"doc": 2},
                permissions={"python-tester": "update", "rest-extension-user": "read"},
            ),
            DefaultMetadata(
                permissions={"python-tester": "update", "qconsole-user": "read"}
            ),
            Document("/temp/doc3.json", {"doc": 3}),
        ],
    )

    assert 200 == response.status_code

    # doc1 should use the first set of default metadata
    docs = client.documents.read(
        ["/temp/doc1.json", "/temp/doc2.json", "/temp/doc3.json"],
        categories=["content", "metadata"],
    )

    doc1 = next(doc for doc in docs if doc.uri == "/temp/doc1.json")
    doc2 = next(doc for doc in docs if doc.uri == "/temp/doc2.json")
    doc3 = next(doc for doc in docs if doc.uri == "/temp/doc3.json")

    _verify_test_metadata_exists(doc1)

    # Verify doc2 uses its own metadata.
    assert 0 == doc2.quality
    assert 0 == len(doc2.collections)
    assert 0 == len(doc2.properties.keys())
    assert 0 == len(doc2.metadata_values.keys())
    perms = doc2.permissions
    assert 2 == len(perms.keys())
    capabilities = perms["python-tester"]
    assert 1 == len(capabilities)
    assert "update" == capabilities[0]
    capabilities = perms["rest-extension-user"]
    assert 1 == len(capabilities)
    assert "read" == capabilities[0]

    # Verify doc3 uses the second set of default metadata.
    assert 0 == doc3.quality
    assert 0 == len(doc3.collections)
    assert 0 == len(doc3.properties.keys())
    assert 0 == len(doc3.metadata_values.keys())
    perms = doc3.permissions
    assert 2 == len(perms.keys())
    capabilities = perms["python-tester"]
    assert 1 == len(capabilities)
    assert "update" == capabilities[0]
    capabilities = perms["qconsole-user"]
    assert 1 == len(capabilities)
    assert "read" == capabilities[0]


def _verify_test_metadata_exists(doc: Document):
    """
    Convenience function for verifying that document metadata contains the metadata
    defined by TEST_METADATA.
    """
    perms = doc.permissions
    assert 2 == len(perms.keys())
    capabilities = perms["python-tester"]
    assert 2 == len(capabilities)
    assert "read" in capabilities
    assert "update" in capabilities
    capabilities = perms["qconsole-user"]
    assert 1 == len(capabilities)
    assert "execute" == capabilities[0]

    collections = doc.collections
    assert 2 == len(collections)
    assert "c1" in collections
    assert "c2" in collections

    props = doc.properties
    assert 3 == len(props.keys())
    assert "world" == props["hello"]
    assert "<can>be embedded</can>" == props["xml"]
    assert 1 == props["number"]

    assert 1 == doc.quality

    values = doc.metadata_values
    assert 2 == len(values.keys())
    assert "value1" == values["key1"]
    assert "value2" == values["key2"]
