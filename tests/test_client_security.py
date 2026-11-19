# Copyright (c) 2023-2026 Progress Software Corporation and/or its subsidiaries or affiliates. All Rights Reserved.


from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from unittest.mock import Mock, patch

import pytest
from requests import Request, Response, Session

from marklogic import Client
from marklogic.cloud_auth import MarkLogicCloudAuth


@pytest.mark.unit
@pytest.mark.parametrize(
    "url",
    ["https://attacker.example/resource", "//attacker.example/resource"],
)
def test_prepare_request_rejects_cross_origin_url(url):
    client = Client("https://marklogic.example", auth=("user", "password"))

    with pytest.raises(ValueError, match="same origin"):
        client.prepare_request(Request("GET", url))


@pytest.mark.unit
def test_prepare_request_accepts_same_origin_absolute_url():
    client = Client("https://marklogic.example", auth=("user", "password"))

    prepared = client.prepare_request(
        Request("GET", "https://marklogic.example/resource")
    )

    assert prepared.url == "https://marklogic.example/resource"


@pytest.mark.unit
@pytest.mark.parametrize("authorization", ["Basic dXNlcjpwYXNz", "Bearer token"])
def test_rebuild_auth_strips_credentials_on_cross_origin_redirect(authorization):
    client = Client("http://marklogic.example", auth=("user", "password"))
    original_request = Request(
        "GET",
        "http://marklogic.example/resource",
        headers={"Authorization": authorization},
    ).prepare()
    redirected_request = Request(
        "GET",
        "https://marklogic.example/resource",
        headers={"Authorization": authorization},
    ).prepare()
    response = Response()
    response.request = original_request

    client.rebuild_auth(redirected_request, response)

    assert "Authorization" not in redirected_request.headers


@pytest.mark.unit
def test_cloud_auth_does_not_retry_401_from_another_origin():
    session = Session()
    token_response = Mock(status_code=200)
    token_response.json.return_value = {"access_token": "initial-token"}

    with patch(
        "marklogic.cloud_auth.Session.request", return_value=token_response
    ) as request_mock:
        auth = MarkLogicCloudAuth(session, "https://marklogic.example", "api-key")
        request_mock.reset_mock()

        prepared_request = Request("GET", "https://attacker.example/resource").prepare()
        response = Response()
        response.status_code = 401
        response.request = prepared_request

        with patch.object(session, "send") as send:
            assert auth._renew_token_if_necessary(response) is None

    request_mock.assert_not_called()
    send.assert_not_called()
    assert "Authorization" not in prepared_request.headers


@pytest.mark.unit
def test_cloud_auth_does_not_send_token_to_cross_origin_redirect_target():
    session = Session()
    token_response = Mock(status_code=200)
    token_response.json.return_value = {"access_token": "initial-token"}

    with patch(
        "marklogic.cloud_auth.Session.request", return_value=token_response
    ) as request_mock:
        client = Client("https://marklogic.example", cloud_api_key="api-key")
        request_mock.reset_mock()

        original_request = Request("GET", "https://marklogic.example/resource").prepare()
        redirected_request = Request(
            "GET",
            "https://attacker.example/resource",
            headers={"Authorization": "Bearer initial-token"},
        ).prepare()
        response = Response()
        response.request = original_request

        client.rebuild_auth(redirected_request, response)
        client.close()

    request_mock.assert_not_called()
    assert "Authorization" not in redirected_request.headers


@pytest.mark.unit
def test_digest_auth_does_not_answer_foreign_origin_challenge_after_redirect():
    class ChallengeHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.server.authorization_headers.append(
                self.headers.get("Authorization")
            )
            self.send_response(401)
            self.send_header(
                "WWW-Authenticate",
                'Digest realm="attacker", nonce="nonce", qop="auth"',
            )
            self.send_header("Content-Length", "0")
            self.end_headers()

        def log_message(self, format, *args):
            pass

    class RedirectHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(302)
            self.send_header("Location", self.server.redirect_url)
            self.send_header("Content-Length", "0")
            self.end_headers()

        def log_message(self, format, *args):
            pass

    challenge_server = ThreadingHTTPServer(
        ("127.0.0.1", 0), ChallengeHandler
    )
    challenge_server.authorization_headers = []
    redirect_server = ThreadingHTTPServer(("127.0.0.1", 0), RedirectHandler)
    redirect_server.redirect_url = (
        f"http://127.0.0.1:{challenge_server.server_port}/challenge"
    )
    threads = [
        Thread(target=server.serve_forever, daemon=True)
        for server in (challenge_server, redirect_server)
    ]
    for thread in threads:
        thread.start()

    client = Client(
        f"http://127.0.0.1:{redirect_server.server_port}",
        digest=("user", "password"),
    )
    try:
        response = client.get("/redirect")
    finally:
        client.close()
        for server in (redirect_server, challenge_server):
            server.shutdown()
            server.server_close()
        for thread in threads:
            thread.join()

    assert response.status_code == 401
    assert challenge_server.authorization_headers == [None]


@pytest.mark.unit
def test_cloud_auth_still_retries_401_from_configured_origin():
    session = Session()
    token_response = Mock(status_code=200)
    token_response.json.side_effect = [
        {"access_token": "initial-token"},
        {"access_token": "renewed-token"},
    ]
    response = Response()
    response.status_code = 401
    response.request = Request("GET", "https://marklogic.example/resource").prepare()
    retry_response = Response()
    retry_response.status_code = 200

    with patch(
        "marklogic.cloud_auth.Session.request", return_value=token_response
    ) as request:
        auth = MarkLogicCloudAuth(session, "https://marklogic.example", "api-key")
        with patch.object(session, "send", return_value=retry_response) as send:
            retried_response = auth._renew_token_if_necessary(response)

    assert retried_response is retry_response
    assert request.call_count == 2
    send.assert_called_once()
    assert response.request.headers["Authorization"] == "Bearer renewed-token"


@pytest.mark.unit
def test_cloud_auth_renews_for_idna_normalized_same_origin():
    session = Session()
    token_response = Mock(status_code=200)
    token_response.json.side_effect = [
        {"access_token": "initial-token"},
        {"access_token": "renewed-token"},
    ]
    response = Response()
    response.status_code = 401
    response.request = Request(
        "GET", "https://xn--bcher-kva.example/resource"
    ).prepare()
    retry_response = Response()
    retry_response.status_code = 200

    with patch(
        "marklogic.cloud_auth.Session.request", return_value=token_response
    ) as request:
        auth = MarkLogicCloudAuth(session, "https://bücher.example", "api-key")
        with patch.object(session, "send", return_value=retry_response) as send:
            retried_response = auth._renew_token_if_necessary(response)

    assert retried_response is retry_response
    assert request.call_count == 2
    send.assert_called_once()
