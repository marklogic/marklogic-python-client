import json

from decimal import Decimal
from marklogic.documents import Document
from requests import Session
from requests_toolbelt.multipart.decoder import MultipartDecoder

"""
Defines an EvalManager class to simplify usage of the "/v1/eval" REST
endpoint defined at https://docs.marklogic.com/REST/POST/v1/eval.
"""


class EvalManager:
    """
    Provides a method to simplify sending an XQuery or
    JavaScript eval request to the eval endpoint.
    """

    def __init__(self, session: Session):
        self._session = session

    def xquery(
        self, xquery: str, vars: dict = None, return_response: bool = False, **kwargs
    ):
        """
        Send an XQuery script to MarkLogic via a POST to the endpoint
        defined at https://docs.marklogic.com/REST/POST/v1/eval.

        :param xquery: an XQuery string
        :param vars: a dict containing variables to include
        :param return_response: boolean specifying if the entire original response
        object should be returned (True) or if only the data should be returned (False)
        upon a success (2xx) response. Note that if the status code of the response is
        not 2xx, then the entire response is always returned.
        """
        if xquery is None:
            raise ValueError("No script found; must specify a xquery")
        return self.__send_request({"xquery": xquery}, vars, return_response, **kwargs)

    def javascript(
        self,
        javascript: str,
        vars: dict = None,
        return_response: bool = False,
        **kwargs
    ):
        """
        Send a JavaScript script to MarkLogic via a POST to the endpoint
        defined at https://docs.marklogic.com/REST/POST/v1/eval.

        :param javascript: a JavaScript string
        :param vars: a dict containing variables to include
        :param return_response: boolean specifying if the entire original response
        object should be returned (True) or if only the data should be returned (False)
        upon a success (2xx) response. Note that if the status code of the response is
        not 2xx, then the entire response is always returned.
        """
        if javascript is None:
            raise ValueError("No script found; must specify a javascript")
        return self.__send_request(
            {"javascript": javascript}, vars, return_response, **kwargs
        )

    def __send_request(
        self, data: dict, vars: dict = None, return_response: bool = False, **kwargs
    ):
        """
        Send a script (XQuery or javascript) and possibly a dict of vars
        to MarkLogic via a POST to the endpoint defined at
        https://docs.marklogic.com/REST/POST/v1/eval.
        """
        if vars is not None:
            data["vars"] = json.dumps(vars)
        response = self._session.post("v1/eval", data=data, **kwargs)
        return (
            self.__process_response(response)
            if response.status_code == 200 and not return_response
            else response
        )

    def __process_response(self, response):
        """
        Process a multipart REST response by putting them in a list and
        transforming each part based on the "X-Primitive" header.
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
            primitive_function = EvalManager.__primitive_value_converters.get(
                primitive_header
            )
            if primitive_function is not None:
                transformed_parts.append(primitive_function(part))
            else:
                transformed_parts.append(part.text)
        return transformed_parts

    __primitive_value_converters = {
        "integer": lambda part: int(part.text),
        "decimal": lambda part: Decimal(part.text),
        "boolean": lambda part: ("False" == part.text),
        "string": lambda part: part.text,
        "map": lambda part: json.loads(part.text),
        "element()": lambda part: part.text,
        "array": lambda part: json.loads(part.text),
        "array-node()": lambda part: json.loads(part.text),
        "object-node()": lambda part: EvalManager.__process_object_node_part(part),
        "document-node()": lambda part: EvalManager.__process_document_node_part(part),
        "binary()": lambda part: Document(
            EvalManager.__get_decoded_uri_from_part(part), part.content
        ),
    }

    def __get_decoded_uri_from_part(part):
        encoding = part.encoding
        return part.headers["X-URI".encode(encoding)].decode(encoding)

    def __process_object_node_part(part):
        if b"X-URI" in part.headers:
            return Document(
                EvalManager.__get_decoded_uri_from_part(part), json.loads(part.text)
            )
        else:
            return json.loads(part.text)

    def __process_document_node_part(part):
        if b"X-URI" in part.headers:
            return Document(EvalManager.__get_decoded_uri_from_part(part), part.text)
        else:
            return part.text
