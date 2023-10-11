import decimal

from marklogic.documents import Document
from requests_toolbelt.multipart.decoder import MultipartDecoder


def test_invoke_xquery_simple(client):
    parts = client.invoke("/simple.xqy")
    __verify_invoke_simple(parts)


def test_invoke_javascript_simple(client):
    parts = client.invoke("/simple.sjs")
    __verify_invoke_simple(parts)


def test_invoke_xquery_simple_vars(client):
    vars = {"word1": "hello", "word2": "world"}
    parts = client.invoke("/simple_vars.xqy", vars)
    __verify_invoke_with_vars(parts)


def test_invoke_javascript_simple_vars(client):
    vars = {"word1": "hello", "word2": "world"}
    parts = client.invoke("/simple_vars.sjs", vars)
    __verify_invoke_with_vars(parts)


def test_invoke_with_return_response(client):
    response = client.invoke("/simple.xqy", return_response=True)
    assert 200 == response.status_code
    parts = MultipartDecoder.from_response(response).parts
    assert 5 == len(parts)


def test_transaction(client):
    locks = None
    with client.transactions.create() as tx:
        client.invoke("/read_doc1.sjs", tx=tx)
        client.invoke("/read_doc2.xqy", tx=tx)
        locks = client.eval(javascript="xdmp.transactionLocks()", tx=tx)

    read_locks = locks[0]["read"]
    assert "/doc1.json" in read_locks
    assert "/doc2.xml" in read_locks


def __verify_invoke_with_vars(parts):
    assert "hello" == parts[0]
    assert "world" == parts[1]
    assert "hello world" == parts[2]


def __verify_invoke_simple(parts):
    assert type(parts[0]) is str
    assert "A" == parts[0]
    assert type(parts[1]) is int
    assert 1 == parts[1]
    assert type(parts[2]) is decimal.Decimal
    assert decimal.Decimal("1.1") == parts[2]
    assert type(parts[3]) is bool
    assert parts[3] is False
    assert type(parts[4]) is Document
    assert "/musicians/logo.png" == parts[4].uri
    assert b"PNG" in parts[4].content
