# Copyright (c) 2023-2025 Progress Software Corporation and/or its subsidiaries or affiliates. All Rights Reserved.


import pytest

from marklogic import Client

BASE_URL = "http://localhost:8030"


@pytest.fixture
def client():
    return Client(BASE_URL, digest=("python-test-user", "password"))


@pytest.fixture
def admin_client():
    return Client(BASE_URL, digest=("python-test-admin", "password"))


@pytest.fixture
def basic_client():
    # requests allows a tuple to be passed when doing basic authentication.
    return Client(BASE_URL, auth=("python-test-user", "password"))


@pytest.fixture
def not_rest_user_client():
    return Client(BASE_URL, digest=("python-not-rest-user", "password"))


@pytest.fixture
def ssl_client():
    return Client(
        host="localhost",
        scheme="https",
        port=8031,
        digest=("python-test-user", "password"),
        verify=False,
    )


@pytest.fixture
def client_with_props():
    return Client(host="localhost", port=8030, username="admin", password="admin")


@pytest.fixture
def cloud_config():
    """
    To run the tests in test_cloud.py, set 'key' to a valid API key. Otherwise, each
    test will be skipped.
    """
    return {
        "host": "support.test.marklogic.cloud",
        "key": "changeme",
    }


@pytest.fixture(autouse=True)
def prepare_test_database(admin_client: Client):
    """
    Deletes any documents created by other tests to ensure a 'clean' database before a
    test runs. Does not delete documents in the 'test-data' collection which is intended
    to contain all the documents loaded by the test-app. A user with the 'admin' role
    is used so that temporal documents can be deleted.
    """
    query = "cts:uris((), (), cts:not-query(cts:collection-query('test-data'))) \
        ! xdmp:document-delete(.)"
    response = admin_client.post(
        "v1/eval",
        headers={"Content-type": "application/x-www-form-urlencoded"},
        data={"xquery": query},
    )
    assert 200 == response.status_code
