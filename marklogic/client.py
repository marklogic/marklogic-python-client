import json
import requests

from decimal import Decimal
from marklogic.cloud_auth import MarkLogicCloudAuth
from marklogic.documents import Document, DocumentManager
from marklogic.eval import EvalManager
from marklogic.rows import RowManager
from marklogic.transactions import TransactionManager
from requests.auth import HTTPDigestAuth
from requests_toolbelt.multipart.decoder import MultipartDecoder
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

    def invoke(
        self, module: str, vars: dict = None, return_response: bool = False, **kwargs
    ):
        """
        Send a script (XQuery or JavaScript) and possibly a dict of vars
        to MarkLogic via a POST to the endpoint defined at
        https://docs.marklogic.com/REST/POST/v1/eval.

        :param module: The URI of a module in the modules database of the app server
        :param vars: a dict containing variables to include
        :param return_response: boolean specifying if the entire original response
        object should be returned (True) or if only the data should be returned (False)
        upon a success (2xx) response. Note that if the status code of the response is
        not 2xx, then the entire response is always returned.
        """
        data = {"module": module}
        if vars is not None:
            data["vars"] = json.dumps(vars)
        response = self.post("v1/invoke", data=data, **kwargs)
        return (
            self.process_multipart_mixed_response(response)
            if response.status_code == 200 and not return_response
            else response
        )

    def process_multipart_mixed_response(self, response):
        """
        Process a multipart REST response by putting them in a list and
        transforming each part based on the "X-Primitive" header.

        :param response: The original multipart/mixed response from a call to a
        MarkLogic server.
        """
        if "Content-Length" in response.headers:
            return None

        parts = MultipartDecoder.from_response(response).parts
        transformed_parts = []
        for part in parts:
            encoding = part.encoding
            primitive_header = part.headers["X-Primitive".encode(encoding)].decode(
                encoding
            )
            primitive_function = Client.__primitive_value_converters.get(
                primitive_header
            )
            if primitive_function is not None:
                transformed_parts.append(primitive_function(part))
            else:
                transformed_parts.append(part.text)
        return transformed_parts

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

    @property
    def transactions(self):
        if not hasattr(self, "_transactions"):
            self._transactions = TransactionManager(self)
        return self._transactions

    @property
    def eval(self):
        if not hasattr(self, "_eval"):
            self._eval = EvalManager(self)
        return self._eval

    __primitive_value_converters = {
        "integer": lambda part: int(part.text),
        "decimal": lambda part: Decimal(part.text),
        "boolean": lambda part: ("False" == part.text),
        "string": lambda part: part.text,
        "map": lambda part: json.loads(part.text),
        "element()": lambda part: part.text,
        "array": lambda part: json.loads(part.text),
        "array-node()": lambda part: json.loads(part.text),
        "object-node()": lambda part: Client.__process_object_node_part(part),
        "document-node()": lambda part: Client.__process_document_node_part(part),
        "binary()": lambda part: Document(
            Client.__get_decoded_uri_from_part(part), part.content
        ),
    }

    def __get_decoded_uri_from_part(part):
        encoding = part.encoding
        return part.headers["X-URI".encode(encoding)].decode(encoding)

    def __process_object_node_part(part):
        if b"X-URI" in part.headers:
            return Document(
                Client.__get_decoded_uri_from_part(part), json.loads(part.text)
            )
        else:
            return json.loads(part.text)

    def __process_document_node_part(part):
        if b"X-URI" in part.headers:
            return Document(Client.__get_decoded_uri_from_part(part), part.text)
        else:
            return part.text
