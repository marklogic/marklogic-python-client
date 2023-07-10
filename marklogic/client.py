import requests
from requests.auth import HTTPDigestAuth
from urllib.parse import urljoin


class Client(requests.Session):
    def __init__(
        self,
        base_url: str = None,
        auth=None,
        digest=None,
        scheme: str = "http",
        verify: bool = True,
        host: str = None,
        port: int = 0,
        username: str = None,
        password: str = None,
    ):
        if base_url:
            self.base_url = base_url
        else:
            self.base_url = f"{scheme}://{host}:{port}"
        super(Client, self).__init__()
        self.verify = verify
        if auth:
            self.auth = auth
        elif digest:
            self.auth = HTTPDigestAuth(digest[0], digest[1])
        else:
            self.auth = HTTPDigestAuth(username, password)

    def request(self, method, url, *args, **kwargs):
        """
        Overrides the requests function to generate the complete URL before the request
        is sent.
        """
        url = urljoin(self.base_url, url)
        return super(Client, self).request(method, url, *args, **kwargs)

    def prepare_request(self, request, *args, **kwargs):
        """
        Overrides the requests function to generate the complete URL before the
        request is prepared. See
        https://requests.readthedocs.io/en/latest/user/advanced/#prepared-requests for
        more information on prepared requests.
        """
        request.url = urljoin(self.base_url, request.url)
        return super(Client, self).prepare_request(request, *args, **kwargs)
