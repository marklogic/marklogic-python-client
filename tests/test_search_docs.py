import json

from requests import Response

from marklogic import Client


def test_structured_json_string_query(client: Client):
    query = json.dumps({"query": {"term-query": {"text": "world"}}})
    docs = client.documents.search(query=query)
    assert len(docs) == 2


def test_structured_json_query(client: Client):
    query = {"query": {"term-query": {"text": "world"}}}
    docs = client.documents.search(query=query)
    assert len(docs) == 2


def test_structured_xml_query(client: Client):
    query = "<query xmlns='http://marklogic.com/appservices/search'>\
        <term-query><text>world</text></term-query></query>"
    docs = client.documents.search(query=query)
    assert len(docs) == 2


def test_serialized_cts_json_query(client: Client):
    query = {"ctsquery": {"wordQuery": {"text": "world"}}}
    docs = client.documents.search(query=query)
    assert len(docs) == 2


def test_serialized_cts_xml_query(client: Client):
    query = "<word-query xmlns='http://marklogic.com/cts'>\
        <text>world</text></word-query>"
    docs = client.documents.search(query=query)
    assert len(docs) == 2


def test_combined_json_query(client: Client):
    options = {"constraint": {"name": "c1", "value": {"element": {"name": "hello"}}}}
    query = {
        "search": {"options": options},
        "qtext": "c1:world",
    }
    docs = client.documents.search(query=query)
    assert len(docs) == 2


def test_combined_xml_query(client: Client):
    query = "<search xmlns='http://marklogic.com/appservices/search'><options>\
        <constraint name='c1'><value><element name='hello'/></value></constraint>\
        </options><qtext>c1:world</qtext></search>"
    docs = client.documents.search(query=query)
    assert len(docs) == 2


def test_qtext_and_start(client: Client):
    docs = client.documents.search(q="world", start=2)
    assert len(docs) == 1, "2 docs match, but start=2, so only 1 should be returned"


def test_qtext_and_page_length(client: Client):
    docs = client.documents.search(q="world", page_length=1)
    assert len(docs) == 1


def test_search_options(client: Client):
    docs = client.documents.search(q="hello:world", options="test-options")
    assert len(docs) == 1
    assert docs[0].uri == "/doc2.xml"
    docs = client.documents.search(q="hello:no matches", options="test-options")
    assert len(docs) == 0


def test_collection(client: Client):
    docs = client.documents.search(
        categories=["content", "collections"], collections=["search-test"]
    )
    assert len(docs) == 2

    doc1 = next(doc for doc in docs if doc.uri == "/doc1.json")
    assert doc1.content is not None
    assert len(doc1.collections) == 2
    assert "test-data" in doc1.collections
    assert "search-test" in doc1.collections

    doc2 = next(doc for doc in docs if doc.uri == "/doc2.xml")
    assert doc2.content is not None
    assert len(doc1.collections) == 2
    assert "test-data" in doc1.collections
    assert "search-test" in doc1.collections


def test_not_rest_user(not_rest_user_client: Client):
    response: Response = not_rest_user_client.documents.search(q="hello")
    assert (
        response.status_code == 403
    ), """The user does not have the rest-reader privilege, so MarkLogic is expected
    to return a 403. And the documents.search method is then expected to return the
    Response so that the user has access to everything in it."""
