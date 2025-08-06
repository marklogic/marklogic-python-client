# Copyright (c) 2023-2025 Progress Software Corporation and/or its subsidiaries or affiliates. All Rights Reserved.


import json
from marklogic.documents import Document


def test_update_dsl_fromDocDescriptors(client):
    doc_uri = "/temp/doc1.json"
    doc_contents = {"hello": "doc1"}
    doc_permissions = [
        {"capability": "read", "roleName": "python-tester"},
        {"capability": "update", "roleName": "python-tester"},
    ]
    update_query_fromDocDescriptors = f"""
        const docDescriptors = [
            {{
                uri:"{doc_uri}",
                doc:'{json.dumps(doc_contents)}',
                permissions: {json.dumps(doc_permissions)}
            }}
        ];
        op.fromDocDescriptors(docDescriptors).write()
    """
    response = client.rows.update(update_query_fromDocDescriptors, return_response=True)
    assert 200 == response.status_code

    docs = client.documents.read([doc_uri])
    doc1 = next(doc for doc in docs if doc.uri == doc_uri)
    assert "application/json" == doc1.content_type
    assert doc1.version_id is not None
    assert doc_contents == doc1.content


def test_update_dsl_remove(admin_client):
    DEFAULT_PERMS = {"python-tester": ["read", "update"]}
    DOC_URI = "/temp/doc1.json"
    response = admin_client.documents.write(
        [Document(DOC_URI, {"doc": 1}, permissions=DEFAULT_PERMS)]
    )

    update_query_remove = 'op.fromDocUris("' + DOC_URI + '").lockForUpdate().remove()'
    response = admin_client.rows.update(update_query_remove, return_response=True)
    assert 200 == response.status_code

    docs = admin_client.documents.read([DOC_URI])
    assert 0 == len(docs)


def test_update_dsl_wrong_path(admin_client):
    DEFAULT_PERMS = {"python-tester": ["read", "update"]}
    DOC_URI = "/temp/doc1.json"
    response = admin_client.documents.write(
        [Document(DOC_URI, {"doc": 1}, permissions=DEFAULT_PERMS)]
    )

    update_query_remove = 'op.fromDocUris("' + DOC_URI + '").lockForUpdate().remove()'
    response = admin_client.rows.query(update_query_remove, return_response=True)
    assert 500 == response.status_code
    assert (
        "Optic plans that perform updates must be sent via HTTP POST to the v1/rows/update endpoint."
        in response.content.decode("utf-8")
    )


def test_update_via_serialized_plan(client):
    DEFAULT_PERMS = {"python-tester": ["read", "update"]}
    DOC_URI = "/temp/doc2.json"
    client.documents.write([Document(DOC_URI, {"doc": 1}, permissions=DEFAULT_PERMS)])
    docs = client.documents.read(DOC_URI)
    assert 1 == len(docs)

    plan = open("tests/remove-uri-plan.json", "rb")
    response = client.rows.update(plan=plan, return_response=True)
    assert 200 == response.status_code
    docs = client.documents.read(DOC_URI)
    assert 0 == len(docs)
