from urllib.parse import urljoin

import requests
from requests.auth import AuthBase

# See https://requests.readthedocs.io/en/latest/user/advanced/#custom-authentication


class MarkLogicCloudAuth(AuthBase):
    def __init__(self, base_url: str, api_key: str, verify):
        self._base_url = base_url
        self._verify = verify
        self._generate_token(api_key)

    def _generate_token(self, api_key: str):
        response = requests.post(
            urljoin(self._base_url, "/token"),
            data={"grant_type": "apikey", "key": api_key},
            verify=self._verify,
        )

        if response.status_code != 200:
            message = f"Unable to generate token; status code: {response.status_code}"
            message = f"{message}; cause: {response.text}"
            raise ValueError(message)

        self._access_token = response.json()["access_token"]

    def __call__(self, r):
        r.headers["Authorization"] = f"Bearer {self._access_token}"
        return r
