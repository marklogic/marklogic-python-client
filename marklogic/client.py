import requests
from marklogic.cloud_auth import MarkLogicCloudAuth
from marklogic.documents import DocumentManager
from marklogic.rows import RowManager
from requests.auth import HTTPDigestAuth
from urllib.parse import urljoin


class Client(requests.Session):
    def __init__(
        self,
        base_url: str = None,
        base_path: str = None,
        auth=None,
        digest=None,
        scheme: str = "http",
        verify: bool = True,
        host: str = None,
        port: int = 0,
        username: str = None,
        password: str = None,
        cloud_api_key: str = None,
        cloud_token_duration: int = 0,
    ):
        super(Client, self).__init__()
        self.verify = verify

        if cloud_api_key:
            port = 443 if port == 0 else port
            scheme = "https"

        self.base_url = base_url if base_url else f"{scheme}://{host}:{port}"
        if base_path:
            self.base_path = base_path if base_path.endswith("/") else base_path + "/"

        if auth:
            self.auth = auth
        elif digest:
            self.auth = HTTPDigestAuth(digest[0], digest[1])
        elif cloud_api_key:
            self.auth = MarkLogicCloudAuth(
                self, self.base_url, cloud_api_key, cloud_token_duration
            )
        else:
            self.auth = HTTPDigestAuth(username, password)

    def request(self, method, url, *args, **kwargs):
        """
        Overrides the requests function to generate the complete URL before the request
        is sent.
        """
        if hasattr(self, "base_path"):
            if url.startswith("/"):
                url = url[1:]
            url = self.base_path + url
        return super(Client, self).request(method, url, *args, **kwargs)

    def prepare_request(self, request, *args, **kwargs):
        """
        Overrides the requests function to generate the complete URL before the
        request is prepared. See
        https://requests.readthedocs.io/en/latest/user/advanced/#prepared-requests for
        more information on prepared requests. Note that this is invoked after the
        'request' method is invoked.
        """
        request.url = urljoin(self.base_url, request.url)
        return super(Client, self).prepare_request(request, *args, **kwargs)

    @property
    def documents(self):
        if not hasattr(self, "_documents"):
            self._documents = DocumentManager(self)
        return self._documents

    @property
    def rows(self):
        if not hasattr(self, "_rows"):
            self._rows = RowManager(self)
        return self._rows
