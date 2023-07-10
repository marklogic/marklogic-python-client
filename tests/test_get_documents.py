from requests_toolbelt.multipart.decoder import MultipartDecoder


def test_get_docs(client):
    """
    Possible future client interface:
    array_of_documents = client.documents.get(uri=[], metadata=True)

    Where each Document in the array would have fields of:
    uri/content/collections/permissions/quality/properties/metadata_values.
    """
    response = client.get(
        "/v1/documents",
        params={
            "uri": ["/doc1.json", "/doc2.xml"],
            "category": ["content", "metadata"],
            "format": "json",  # Applies only to metadata
        },
        headers={"Accept": "multipart/mixed"},
    )

    assert 200 == response.status_code

    # Could provide a class for converting a multipart/mixed response into an array
    # of documents too:
    # from marklogic import DocumentDecoder
    # array_of_documents = DocumentDecoder.from_response(response)
    decoder = MultipartDecoder.from_response(response)
    for part in decoder.parts:
        print(part.headers)
        print(part.text)


def test_search_docs(client_with_props):
    response = client_with_props.get(
        "v1/search",
        params={
            "collection": "test-data",
            "category": ["content", "metadata"],
            "format": "json",  # Applies only to metadata
        },
        headers={"Accept": "multipart/mixed"},  # Indicates we want documents back.
    )

    for part in MultipartDecoder.from_response(response).parts:
        print(part.headers)
        print(part.text)


def test_get_docs_basic_auth(basic_client):
    # Just verifies that basic auth works as expected.
    response = basic_client.get("/v1/documents", params={"uri": "/doc1.json"})
    assert 200 == response.status_code
    assert "world" == response.json()["hello"]
