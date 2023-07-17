from marklogic import Client
from marklogic.documents import Document, DefaultMetadata

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
        [
            Document(
                "/temp/doc1.json",
                {"content": "original"},
                *TEST_METADATA.values(),
            ),
        ]
    )
    assert 200 == response.status_code

    metadata = _get_metadata(client, "/temp/doc1.json")
    _verify_test_metadata_exists(metadata)


def test_only_quality_and_permissions(client: Client):
    response = client.documents.write(
        [
            Document(
                "/temp/doc1.json",
                {"doc": 1},
                permissions={
                    "python-tester": ["read", "update"],
                    "qconsole-user": "execute",
                },
                quality=2,
            ),
        ]
    )

    assert 200 == response.status_code

    metadata = _get_metadata(client, "/temp/doc1.json")
    assert 2 == metadata["quality"]
    assert 0 == len(metadata["collections"])
    assert 0 == len(metadata["properties"].keys())
    assert 0 == len(metadata["metadataValues"].keys())


def test_only_quality(client: Client):
    response = client.documents.write(
        [
            Document(
                "/temp/doc1.json",
                {"doc": 1},
                quality=2,
            ),
        ]
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
                permissions={"python-tester": "update", "rest-extension-user": "read"}
            ),
            DefaultMetadata(
                permissions={"python-tester": "update", "qconsole-user": "read"}
            ),
            Document("/temp/doc3.json", {"doc": 3}),
        ],
    )

    assert 200 == response.status_code

    # doc1 should use the first set of default metadata
    metadata = _get_metadata(client, "/temp/doc1.json")
    _verify_test_metadata_exists(metadata)

    # doc2 should use its own metadata
    metadata = _get_metadata(client, "/temp/doc2.json")
    assert 0 == metadata["quality"]
    assert 0 == len(metadata["collections"])
    assert 0 == len(metadata["properties"].keys())
    assert 0 == len(metadata["metadataValues"].keys())
    perms = metadata["permissions"]
    assert 2 == len(perms)
    perm = next(perm for perm in perms if perm["role-name"] == "python-tester")
    assert 1 == len(perm["capabilities"])
    assert "update" in perm["capabilities"]
    perm = next(perm for perm in perms if perm["role-name"] == "rest-extension-user")
    assert 1 == len(perm["capabilities"])
    assert "read" in perm["capabilities"]

    # doc3 should use the second set of default metadata
    metadata = _get_metadata(client, "/temp/doc3.json")
    assert 0 == metadata["quality"]
    assert 0 == len(metadata["collections"])
    assert 0 == len(metadata["properties"].keys())
    assert 0 == len(metadata["metadataValues"].keys())
    perms = metadata["permissions"]
    assert 2 == len(perms)
    perm = next(perm for perm in perms if perm["role-name"] == "python-tester")
    assert 1 == len(perm["capabilities"])
    assert "update" in perm["capabilities"]
    perm = next(perm for perm in perms if perm["role-name"] == "qconsole-user")
    assert 1 == len(perm["capabilities"])
    assert "read" in perm["capabilities"]



def _get_metadata(client: Client, uri: str):
    return client.get(f"v1/documents?uri={uri}&category=metadata&format=json").json()


def _verify_test_metadata_exists(metadata: dict):
    """
    Convenience function for verifying that document metadata contains the metadata
    defined by TEST_METADATA.
    """
    perms = metadata["permissions"]
    assert 2 == len(perms)
    perm = next(perm for perm in perms if perm["role-name"] == "python-tester")
    assert 2 == len(perm["capabilities"])
    assert "read" in perm["capabilities"]
    assert "update" in perm["capabilities"]
    perm = next(perm for perm in perms if perm["role-name"] == "qconsole-user")
    assert 1 == len(perm["capabilities"])
    assert "execute" == perm["capabilities"][0]

    collections = metadata["collections"]
    assert 2 == len(collections)
    assert "c1" in collections
    assert "c2" in collections

    props = metadata["properties"]
    assert 3 == len(props.keys())
    assert "world" == props["hello"]
    assert "<can>be embedded</can>" == props["xml"]
    assert 1 == props["number"]

    assert 1 == metadata["quality"]

    values = metadata["metadataValues"]
    assert 2 == len(values.keys())
    assert "value1" == values["key1"]
    assert "value2" == values["key2"]
