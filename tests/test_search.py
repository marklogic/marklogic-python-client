def test_search(test_session):
    response = test_session.get("http://localhost:8030/v1/search")
    assert 200 == response.status_code
    assert "application/xml; charset=utf-8" == response.headers["Content-type"]
    assert response.text.startswith("<search:response")
