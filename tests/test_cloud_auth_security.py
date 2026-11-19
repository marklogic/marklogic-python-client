# Copyright (c) 2023-2026 Progress Software Corporation and/or its subsidiaries or affiliates. All Rights Reserved.


import pytest

from marklogic import Client
from marklogic.cloud_auth import MarkLogicCloudAuth
from marklogic.cloud_auth import DEFAULT_TOKEN_REQUEST_TIMEOUT


@pytest.fixture(autouse=True)
def prepare_test_database():
    """Override integration fixture from conftest for isolated unit tests."""
    return


class _TokenResponse:
    status_code = 200
    text = ""

    @staticmethod
    def json():
        return {"access_token": "token-value"}


class _RequestStub:
    def __init__(self, url):
        self.url = url
        self.headers = {}


class _ResponseStub:
    def __init__(self, status_code, url):
        self.status_code = status_code
        self.request = _RequestStub(url)


def test_cloud_api_key_rejects_http_base_url():
    with pytest.raises(ValueError) as err:
        Client(base_url="http://example.com", cloud_api_key="k")

    assert "base_url must use HTTPS when cloud_api_key is provided." == str(
        err.value
    )


def test_cloud_token_request_has_timeout(monkeypatch):
    observed_method = None
    observed_timeout = None
    observed_url = None
    observed_auth = None

    def fake_request(self, method, url, *args, **kwargs):
        nonlocal observed_method
        nonlocal observed_timeout
        nonlocal observed_url
        nonlocal observed_auth
        observed_method = method
        observed_timeout = kwargs.get("timeout")
        observed_url = url
        observed_auth = kwargs.get("auth")
        return _TokenResponse()

    monkeypatch.setattr("requests.sessions.Session.request", fake_request)

    Client(host="example.com", cloud_api_key="k")

    assert "POST" == observed_method
    assert DEFAULT_TOKEN_REQUEST_TIMEOUT == observed_timeout
    assert "https://example.com:443/token" == observed_url
    request = _RequestStub("https://example.com:443/token")
    assert callable(observed_auth)
    observed_auth(request)
    assert "Authorization" not in request.headers


def test_cloud_token_request_ignores_base_path(monkeypatch):
    observed_url = None

    def fake_request(self, method, url, *args, **kwargs):
        nonlocal observed_url
        observed_url = url
        return _TokenResponse()

    monkeypatch.setattr("requests.sessions.Session.request", fake_request)

    Client(
        host="example.com",
        cloud_api_key="k",
        base_path="/ml/test/marklogic/manage",
    )

    assert "https://example.com:443/token" == observed_url


def test_cloud_api_key_warns_when_verify_disabled(monkeypatch):
    def fake_request(self, method, url, *args, **kwargs):
        return _TokenResponse()

    monkeypatch.setattr("requests.sessions.Session.request", fake_request)

    with pytest.warns(UserWarning, match="verify=False"):
        Client(host="example.com", cloud_api_key="k", verify=False)


def test_renewal_guard_not_reset_by_token_response():
    auth = MarkLogicCloudAuth.__new__(MarkLogicCloudAuth)
    auth.resent_request_on_401 = False
    auth._access_token = "old-token"
    auth._base_url = "https://example.com:443"

    first_401 = _ResponseStub(401, "https://example.com:443/v1/search")
    token_200 = _ResponseStub(200, "https://example.com:443/token")
    second_401 = _ResponseStub(401, "https://example.com:443/v1/search")
    token_renewals = 0

    class _SessionStub:
        def __init__(self):
            self.send_calls = 0

        def send(self, request, *args, **kwargs):
            self.send_calls += 1
            if self.send_calls > 1:
                raise AssertionError("Token was renewed more than once")
            auth._renew_token_if_necessary(second_401)
            return second_401

    def fake_generate_token():
        nonlocal token_renewals
        token_renewals += 1
        auth._access_token = f"new-token-{token_renewals}"
        auth._renew_token_if_necessary(token_200)

    auth._session = _SessionStub()
    auth._generate_token = fake_generate_token

    retried_response = auth._renew_token_if_necessary(first_401)

    assert retried_response is second_401
    assert 1 == token_renewals
    assert 1 == auth._session.send_calls
    assert False is auth.resent_request_on_401
    assert "Bearer new-token-1" == first_401.request.headers["Authorization"]