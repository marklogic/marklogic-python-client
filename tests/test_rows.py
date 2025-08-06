# Copyright (c) 2023-2025 Progress Software Corporation and/or its subsidiaries or affiliates. All Rights Reserved.


from pytest import raises
from marklogic.documents import Document
import uuid


dsl_query = 'op.fromView("test","musician").orderBy(op.col("lastName"))'
serialized_query = '{"$optic":{"ns":"op", "fn":"operators", "args":[{"ns":"op", "fn":"from-view", "args":["test", "musician"]}, {"ns":"op", "fn":"order-by", "args":[{"ns":"op", "fn":"col", "args":["lastName"]}]}]}}'
sql_query = "select * from musician order by lastName"
sparql_query = "PREFIX musician: <http://marklogic.com/column/test/musician/> SELECT * WHERE {?s musician:lastName ?lastName} ORDER BY ?lastName"


def test_dsl_default(client):
    data = client.rows.query(dsl_query)
    verify_four_musicians_are_returned_in_json(data, "test.musician.lastName")


def test_no_rows_returned(client):
    query = 'op.fromView("test", "musician").where(op.eq(op.col("lastName"), "Smith"))'
    results = client.rows.query(query)
    assert results is None


def test_dsl_default_return_response(client):
    response = client.rows.query(dsl_query, return_response=True)
    assert 200 == response.status_code
    verify_four_musicians_are_returned_in_json(
        response.json(), "test.musician.lastName"
    )


def test_query_bad_user(not_rest_user_client):
    response = not_rest_user_client.rows.query(dsl_query)
    assert 403 == response.status_code


def test_dsl_json(client):
    data = client.rows.query(dsl_query, format="json")
    verify_four_musicians_are_returned_in_json(data, "test.musician.lastName")


def test_dsl_xml(client):
    data = client.rows.query(dsl_query, format="xml")
    verify_four_musicians_are_returned_in_xml_string(data)


def test_dsl_csv(client):
    data = client.rows.query(dsl_query, format="csv")
    verify_four_musicians_are_returned_in_csv(data)


def test_dsl_json_seq(client):
    data = client.rows.query(dsl_query, format="json-seq")
    verify_four_musicians_are_returned_in_json_seq(data)


def test_invalid_format(client):
    with raises(
        ValueError, match="Invalid value for 'format' argument: invalid; must be one of"
    ):
        client.rows.query(dsl_query, format="invalid")


def test_serialized_default(client):
    data = client.rows.query(plan=serialized_query)
    verify_four_musicians_are_returned_in_json(data, "test.musician.lastName")


def test_sql_default(client):
    data = client.rows.query(sql=sql_query)
    verify_four_musicians_are_returned_in_json(data, "test.musician.lastName")


def test_sparql_default(client):
    data = client.rows.query(sparql=sparql_query)
    verify_four_musicians_are_returned_in_json(data, "lastName")


def test_no_query_parameter_provided(client):
    with raises(
        ValueError,
        match="No query found; must specify one of: dsl, plan, sql, or sparql",
    ):
        client.rows.query()


def test_transaction(client):
    lastName = str(uuid.uuid4())
    content = {
        "musician": {
            "lastName": lastName,
            "firstName": "DoesntMatter",
            "dob": "2000-01-01",
        }
    }
    uri = "/temp/musician5.json"

    with client.transactions.create() as tx:
        query = f'op.fromView("test", "musician")'
        query = f'{query}.where(op.eq(op.col("lastName"), "{lastName}"))'
        results = client.rows.query(query, tx=tx)
        assert results is None

        perms = {"python-tester": ["read", "update"]}
        doc = Document(uri, content, permissions=perms)
        client.documents.write(doc, tx=tx)

        results = client.rows.query(query, tx=tx)
        assert len(results["rows"]) == 1

        client.delete("/v1/documents", params={"uri": uri, "txid": tx.id})
        results = client.rows.query(query, tx=tx)
        assert results is None


def verify_four_musicians_are_returned_in_json(data, column_name):
    assert type(data) is dict
    assert 4 == len(data["rows"])
    for index, musician in enumerate(["Armstrong", "Byron", "Coltrane", "Davis"]):
        assert {"type": "xs:string", "value": musician} == data["rows"][index][
            column_name
        ]


def verify_four_musicians_are_returned_in_xml_string(data):
    assert type(data) is str
    assert 4 == data.count('lastName" type="xs:string">')
    for musician in ["Armstrong", "Byron", "Coltrane", "Davis"]:
        assert 'lastName" type="xs:string">' + musician in data


def verify_four_musicians_are_returned_in_csv(data):
    assert type(data) is str
    assert 5 == len(data.split("\n"))
    for musician in [
        "Armstrong,Louis,1901-08-04",
        "Byron,Don,1958-11-08",
        "Coltrane,John,1926-09-23",
        "Davis,Miles,1926-05-26",
    ]:
        assert musician in data


def verify_four_musicians_are_returned_in_json_seq(data):
    assert type(data) is str
    rows = data.split("\n")
    assert 6 == len(rows)
    for musician in ["Armstrong", "Byron", "Coltrane", "Davis"]:
        assert 'lastName":{"type":"xs:string","value":"' + musician in data
