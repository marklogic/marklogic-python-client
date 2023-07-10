def test_search(client):
    response = client.get("v1/search")
    assert 200 == response.status_code
    assert "application/xml; charset=utf-8" == response.headers["Content-type"]
    assert response.text.startswith("<search:response")
