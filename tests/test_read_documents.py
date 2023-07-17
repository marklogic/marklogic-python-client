from requests import Response

from marklogic import Client
from marklogic.documents import Document

DEFAULT_PERMS = {"python-tester": ["read", "update"]}


def test_write_and_read_binary(client: Client):
    content = "MarkLogic and Python".encode("ascii")
    response = client.documents.write(
        [
            Document(
                "/temp/doc1.bin",
                content,
                permissions=DEFAULT_PERMS,
            )
        ]
    )
    assert 200 == response.status_code

    docs = client.documents.read(["/temp/doc1.bin"])
    assert len(docs) == 1
    doc = docs[0]
    assert doc.uri == "/temp/doc1.bin"
    content = doc.content.decode("ascii")
    assert content == "MarkLogic and Python"


def test_read_uri_with_double_quotes(client: Client):
    uri = '/this/"works.json'
    response = client.documents.write(
        [Document(uri, {"hello": "world"}, permissions=DEFAULT_PERMS)]
    )
    assert response.status_code == 200

    docs = client.documents.read(["/this/%22works.json"])
    assert len(docs) == 1
    assert "/this/%22works.json" == docs[0].uri


def test_uri_not_found(client: Client):
    docs = client.documents.read(["/doesnt-exist.json"])
    assert docs is not None
    assert len(docs) == 0


def test_read_with_transform(client: Client):
    """
    Verifies a user can pass in any kwargs and they will be retained as request
    parameters, along with the ones added by the client.
    """
    docs = client.documents.read(
        ["/doc1.json"],
        categories=["content", "metadata"],
        params={"transform": "envelope"},
    )
    assert 1 == len(docs)
    assert docs[0].content == {"envelope": {"hello": "world"}}


def test_read_only_collections(client: Client):
    docs = client.documents.read(
        ["/doc1.json", "/doc2.xml"], categories=["collections"]
    )
    assert 2 == len(docs)

    doc1 = docs[0]
    assert doc1.uri == "/doc1.json"
    assert len(doc1.collections) == 1
    assert doc1.collections[0] == "test-data"
    assert doc1.content is None
    assert doc1.permissions is None
    assert doc1.quality is None
    assert doc1.metadata_values is None
    assert doc1.properties is None

    doc2 = docs[1]
    assert doc2.uri == "/doc2.xml"
    assert len(doc2.collections) == 1
    assert doc2.collections[0] == "test-data"
    assert doc2.content is None
    assert doc2.permissions is None
    assert doc2.quality is None
    assert doc2.metadata_values is None
    assert doc2.properties is None


def test_with_accept_header(client: Client):
    """
    Verifies that any Accept header provided by the user will be ignored, as it's
    expected to be set to multipart/mixed by the client.
    """
    docs = client.documents.read(
        ["/doc1.json"],
        headers={"Accept": "something/invalid"},
        categories=["content", "quality"],
    )

    assert len(docs) == 1
    doc = docs[0]
    assert doc.uri == "/doc1.json"
    assert doc.content == {"hello": "world"}
    assert doc.quality == 0
    assert doc.collections is None


def test_read_with_basic_client(basic_client: Client):
    # Just verifies that basic auth works as expected.
    doc = basic_client.documents.read(["/doc1.json"])[0]
    assert {"hello": "world"} == doc.content


def test_not_rest_user(not_rest_user_client: Client):
    response: Response = not_rest_user_client.documents.read(
        ["/doc1.json", "/doc2.xml"]
    )
    assert (
        response.status_code == 403
    ), """The user does not have the rest-reader privilege, so MarkLogic is expected
    to return a 403. And the documents.read method is then expected to return the
    Response so that the user has access to everything in it."""
