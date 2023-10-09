import decimal

from marklogic.documents import Document
from requests_toolbelt.multipart.decoder import MultipartDecoder


def test_xquery_common_primitives(client):
    parts = client.eval.xquery(
        """(
        'A', 1, 1.1, fn:false(), fn:doc('/musicians/logo.png'))
        """
    )
    __verify_common_primitives(parts)


def test_javascript_common_primitives(client):
    parts = client.eval.javascript(
        """xdmp.arrayValues([
        'A', 1, 1.1, false, fn.doc('/musicians/logo.png')
        ])"""
    )
    __verify_common_primitives(parts)


def test_xquery_specific_primitives(client):
    parts = client.eval.xquery(
        """(
        <hello>world</hello>,
        object-node {'A': 'a'},
        fn:doc('/doc2.xml'),
        document {<test/>},
        array-node {1, "23", 4}
        )"""
    )
    assert type(parts[0]) is str
    assert "<hello>world</hello>" == parts[0]
    assert type(parts[1]) is dict
    assert {"A": "a"} == parts[1]
    assert type(parts[2]) is Document
    assert "/doc2.xml" == parts[2].uri
    assert "<hello>world</hello>" in parts[2].content
    assert type(parts[3]) is str
    assert '<?xml version="1.0" encoding="UTF-8"?>\n<test/>' == parts[3]
    assert type(parts[4]) is list
    assert "23" == parts[4][1]
    assert 3 == len(parts[4])


def test_javascript_specific_primitives(client):
    parts = client.eval.javascript(
        """xdmp.arrayValues([
        {'A': 'a'},
        ['Z', 'Y', 1],
        fn.head(cts.search('Armstrong'))
        ])"""
    )
    assert type(parts[0]) is dict
    assert {"A": "a"} == parts[0]
    assert type(parts[1]) is list
    assert "Z" == parts[1][0]
    assert 3 == len(parts[1])
    assert type(parts[2]) is Document
    assert "/musicians/musician1.json" == parts[2].uri
    assert {
        "musician": {
            "lastName": "Armstrong",
            "firstName": "Louis",
            "dob": "1901-08-04",
            "instrument": ["trumpet", "vocal"],
        }
    } == parts[2].content


def test_xquery_with_return_response(client):
    response = client.eval.xquery("('A', 1, 1.1, fn:false())", return_response=True)
    assert 200 == response.status_code
    parts = MultipartDecoder.from_response(response).parts
    assert 4 == len(parts)


def test_xquery_vars(client):
    vars = {"word1": "hello", "word2": "world"}
    script = """
    xquery version "1.0-ml";
    declare variable $word1 as xs:string external;
    declare variable $word2 as xs:string external;
    fn:concat($word1, " ", $word2)
    """
    parts = client.eval.xquery(script, vars)
    assert type(parts[0]) is str
    assert "hello world" == parts[0]


def test_javascript_vars(client):
    vars = {"word1": "hello", "word2": "world"}
    parts = client.eval.javascript("xdmp.arrayValues([word1, word2])", vars)
    assert type(parts[0]) is str
    assert "hello" == parts[0]


def test_xquery_empty_sequence(client):
    parts = client.eval.xquery("()")
    assert parts is None


def test_javascript_script(client):
    parts = client.eval.javascript("[]")
    assert [[]] == parts


def __verify_common_primitives(parts):
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
