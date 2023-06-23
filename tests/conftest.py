import pytest
import requests
from requests.auth import HTTPDigestAuth


@pytest.fixture
def test_session():
    session = requests.Session()
    session.auth = HTTPDigestAuth("python-test-user", "password")
    return session
