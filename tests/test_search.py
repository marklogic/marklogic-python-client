import requests
from requests.auth import HTTPDigestAuth


def test_search():
    response = requests.get(
        "http://localhost:8030/v1/search",
        auth=HTTPDigestAuth("python-test-user", "password")
    )
    assert 200 == response.status_code
    assert "application/xml; charset=utf-8" == response.headers["Content-type"]
    assert response.text.startswith("<search:response")
