# Copyright (c) 2023-2025 Progress Software Corporation and/or its subsidiaries or affiliates. All Rights Reserved.


import logging
import requests
from requests import Response, Session, Request
from requests.auth import AuthBase
from urllib.parse import urljoin

logger = logging.getLogger(__name__)


class MarkLogicCloudAuth(AuthBase):
    """
    Handles authenticating with Progress Data Cloud.
    See https://requests.readthedocs.io/en/latest/user/advanced/#custom-authentication
    for more information on custom authentication classes in requests.

    Requires an instance of Session so that when a 401 is received on a request to
    MarkLogic - which may indicate that the token has expired - a new token can be
    generated and the original request can be resent using the same Session that
    initially sent it.
    """

    def __init__(
        self,
        session: Session,
        base_url: str,
        api_key: str,
        cloud_token_duration: int = 0,
    ):
        self._session = session
        self._base_url = base_url
        self._api_key = api_key
        self._cloud_token_duration = cloud_token_duration
        self._generate_token()

        # See https://docs.python-requests.org/en/latest/user/advanced/#event-hooks for
        # more information on requests hooks.
        self._session.hooks["response"].append(self._renew_token_if_necessary)

        # Used for keeping track of whether a request has been resent with a new token
        # after receiving a 401; avoids an infinite loop of retrying requests.
        self.resent_request_on_401 = False

    def __call__(self, request: Request):
        # Invoked via the requests authentication framework.
        self._add_authorization_header(request)
        return request

    def _generate_token(self):
        params = {}
        if self._cloud_token_duration > 0:
            params["duration"] = self._cloud_token_duration

        response = requests.post(
            urljoin(self._base_url, "/token"),
            data={"grant_type": "apikey", "key": self._api_key},
            verify=self._session.verify,
            params=params,
        )

        if response.status_code != 200:
            message = f"Unable to generate token; status code: {response.status_code}"
            message = f"{message}; cause: {response.text}"
            raise ValueError(message)

        self._access_token = response.json()["access_token"]

    def _renew_token_if_necessary(self, response: Response, *args, **kwargs):
        if response.status_code == 401 and not self.resent_request_on_401:
            logger.debug("Received 401; will generate new token and try request again")
            self.resent_request_on_401 = True
            self._generate_token()
            self._add_authorization_header(response.request)
            return self._session.send(response.request, *args, **kwargs)
        self.resent_request_on_401 = False

    def _add_authorization_header(self, request: Request) -> None:
        request.headers["Authorization"] = f"Bearer {self._access_token}"
