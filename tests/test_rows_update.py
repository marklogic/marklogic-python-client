import json

doc_contents = {"hello": "doc1"}
doc_uri = "/doc1.json"
update_query_fromDocDescriptors = (
    'const docDescriptors = [{ uri:"'
    + doc_uri
    + '", doc:'
    + json.dumps(doc_contents)
    + "}]; op.fromDocDescriptors(docDescriptors).write()"
)
update_query_remove = 'op.fromDocUris("' + doc_uri + '").lockForUpdate().remove()'


def test_update_dsl_fromDocDescriptors(admin_client):
    response = admin_client.rows.update(
        update_query_fromDocDescriptors, return_response=True
    )
    assert 200 == response.status_code

    docs = admin_client.documents.read([doc_uri])
    doc1 = next(doc for doc in docs if doc.uri == doc_uri)
    assert "application/json" == doc1.content_type
    assert doc1.version_id is not None
    assert doc_contents == doc1.content


def test_update_dsl_remove(admin_client):
    response = admin_client.rows.update(
        update_query_fromDocDescriptors, return_response=True
    )
    assert 200 == response.status_code

    response = admin_client.rows.update(update_query_remove, return_response=True)
    assert 200 == response.status_code

    docs = admin_client.documents.read([doc_uri])
    assert 0 == len(docs)
