import pytest
from marklogic.client import Client


@pytest.fixture
def client():
    return Client("http://localhost:8030", digest=("python-test-user", "password"))


@pytest.fixture
def basic_client():
    # requests allows a tuple to be passed when doing basic authentication.
    return Client("http://localhost:8030", auth=("python-test-user", "password"))


@pytest.fixture
def ssl_client():
    return Client(host="localhost", scheme="https", port=8031,
                  digest=("python-test-user", "password"),
                  verify=False)


@pytest.fixture
def client_with_props():
    return Client(host="localhost", port=8030, username="admin", password="admin")
