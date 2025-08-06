# Copyright (c) 2023-2025 Progress Software Corporation and/or its subsidiaries or affiliates. All Rights Reserved.


import logging
import pytest
import time

from marklogic import Client

"""
This module is intended for manual testing where the cloud_config fixture
in conftest.py is modified to have a real API key and not "changeme" as a value.
"""

DEFAULT_BASE_PATH = "/ml/test/marklogic/manage"


def test_base_path_doesnt_end_with_slash(cloud_config):
    if cloud_config["key"] == "changeme":
        return

    client = _new_client(cloud_config, DEFAULT_BASE_PATH)
    _verify_client_works(client)


def test_base_path_ends_with_slash(cloud_config):
    if cloud_config["key"] == "changeme":
        return

    client = _new_client(cloud_config, DEFAULT_BASE_PATH + "/")
    _verify_client_works(client)


def test_base_url_used_instead_of_host(cloud_config):
    if cloud_config["key"] == "changeme":
        return

    base_url = f"https://{cloud_config['host']}"
    client = Client(
        base_url, cloud_api_key=cloud_config["key"], base_path=DEFAULT_BASE_PATH
    )
    _verify_client_works(client)


def test_invalid_host():
    with pytest.raises(ValueError) as err:
        Client(
            host="localhost",
            port=8031,
            verify=False,
            cloud_api_key="doesnt-matter-for-this-test",
            base_path=DEFAULT_BASE_PATH,
        )
    assert "Unable to generate token; status code: 401; cause: " in str(err.value)


def test_invalid_api_key(cloud_config):
    if cloud_config["key"] == "changeme":
        return

    with pytest.raises(ValueError) as err:
        Client(
            host=cloud_config["host"],
            cloud_api_key="invalid-api-key",
            base_path=DEFAULT_BASE_PATH,
        )
    assert (
        'Unable to generate token; status code: 401; cause: {"statusCode":401,"errorMessage":"API Key is not valid."}'
        == str(err.value)
    )


@pytest.mark.skip(
    "Skipped since it takes over a minute to run; comment this out to run it."
)
def test_renew_token(cloud_config):
    if cloud_config["key"] == "changeme":
        return

    client = Client(
        host=cloud_config["host"],
        cloud_api_key=cloud_config["key"],
        cloud_token_duration=1,
        base_path=DEFAULT_BASE_PATH,
    )

    _verify_client_works(client)

    logging.info("Sleeping to ensure the token will have expired on the next call")
    time.sleep(61)

    # First call should fail, resulting in a new token being generated.
    _verify_client_works(client)


def _new_client(cloud_config, base_path: str) -> Client:
    return Client(
        host=cloud_config["host"],
        cloud_api_key=cloud_config["key"],
        base_path=base_path,
    )


def _verify_client_works(client):
    # Verify that the request works regardless of whether the path starts with a slash
    # or not.
    _verify_search_response(client.get("v1/search?format=json"))
    _verify_search_response(client.get("/v1/search?format=json"))


def _verify_search_response(response):
    assert 200 == response.status_code
    assert 1 == response.json()["start"]
