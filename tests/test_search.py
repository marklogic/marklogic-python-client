import requests
from requests.auth import HTTPDigestAuth


def test_get_search_response_with_no_args():
    response = requests.get(
        "http://localhost:8030/v1/search", auth=HTTPDigestAuth("admin", "admin")
    )
    assert 200 == response.status_code
    assert "application/xml; charset=utf-8" == response.headers["Content-type"]
    assert response.text.startswith("<search:response")
