from marklogic import Client
from marklogic.documents import Document


def test_all_metadata(client: Client):
    uri = "/temp/doc1.json"

    response = client.documents.write(
        [
            Document(
                uri,
                {"content": "original"},
                collections=["c1", "c2"],
                permissions={
                    "python-tester": ["read", "update"],
                    "qconsole-user": "execute",
                },
                quality=1,
                properties={
                    "hello": "world",
                    "xml": "<can>be embedded</can>",
                    "number": 1,
                },
                metadata_values={"key1": "value1", "key2": "value2"},
            ),
        ]
    )

    assert 200 == response.status_code

    # Get and verify all the metadata.
    metadata = client.get(
        "v1/documents?uri=/temp/doc1.json&category=metadata&format=json"
    ).json()

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

    metadata = client.get(
        "v1/documents?uri=/temp/doc1.json&category=metadata&format=json"
    ).json()

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
