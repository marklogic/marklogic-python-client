# Copyright (c) 2023-2025 Progress Software Corporation and/or its subsidiaries or affiliates. All Rights Reserved.


import json
import requests

from marklogic.cloud_auth import MarkLogicCloudAuth
from marklogic.documents import DocumentManager
from marklogic.internal.eval import process_multipart_mixed_response
from marklogic.rows import RowManager
from marklogic.transactions import TransactionManager, Transaction
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
            self._documents = DocumentManager(session=self)
        return self._documents

    @property
    def rows(self):
        if not hasattr(self, "_rows"):
            self._rows = RowManager(session=self)
        return self._rows

    @property
    def transactions(self):
        if not hasattr(self, "_transactions"):
            self._transactions = TransactionManager(session=self)
        return self._transactions

    def eval(
        self,
        javascript: str = None,
        xquery: str = None,
        vars: dict = None,
        tx: Transaction = None,
        return_response: bool = False,
        **kwargs,
    ):
        """
        Send a script to MarkLogic via a POST to the endpoint
        defined at https://docs.marklogic.com/REST/POST/v1/eval. Must define either
        'javascript' or 'xquery'. Returns a list, unless no content is returned in
        which case None is returned.

        :param javascript: a JavaScript script
        :param xquery: an XQuery script
        :param vars: a dict containing variables to include
        :param tx: optional REST transaction in which to service this request.
        :param return_response: boolean specifying if the entire original response
        object should be returned (True) or if only the data should be returned (False)
        upon a success (2xx) response. Note that if the status code of the response is
        not 2xx, then the entire response is always returned.
        """
        data = {}
        if javascript:
            data = {"javascript": javascript}
        elif xquery:
            data = {"xquery": xquery}
        else:
            raise ValueError("Must define either 'javascript' or 'xquery' argument.")
        if vars:
            data["vars"] = json.dumps(vars)
        params = kwargs.pop("params", {})
        if tx:
            params["txid"] = tx.id
        response = self.post("v1/eval", data=data, params=params, **kwargs)
        return (
            process_multipart_mixed_response(response)
            if response.status_code == 200 and not return_response
            else response
        )

    def invoke(
        self,
        module: str,
        vars: dict = None,
        tx: Transaction = None,
        return_response: bool = False,
        **kwargs,
    ):
        """
        Send a script (XQuery or JavaScript) and possibly a dict of vars
        to MarkLogic via a POST to the endpoint defined at
        https://docs.marklogic.com/REST/POST/v1/eval. Returns a list, unless no content
        is returned in which case None is returned.

        :param module: The URI of a module in the modules database of the app server
        :param vars: a dict containing variables to include
        :param tx: optional REST transaction in which to service this request.
        :param return_response: boolean specifying if the entire original response
        object should be returned (True) or if only the data should be returned (False)
        upon a success (2xx) response. Note that if the status code of the response is
        not 2xx, then the entire response is always returned.
        """
        data = {"module": module}
        if vars:
            data["vars"] = json.dumps(vars)
        params = kwargs.pop("params", {})
        if tx:
            params["txid"] = tx.id
        response = self.post("v1/invoke", data=data, params=params, **kwargs)
        return (
            process_multipart_mixed_response(response)
            if response.status_code == 200 and not return_response
            else response
        )
