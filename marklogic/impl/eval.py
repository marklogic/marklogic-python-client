import json

from decimal import Decimal
from marklogic.documents import Document
from requests import Response
from requests_toolbelt.multipart.decoder import MultipartDecoder

"""
Supports working with data returned by the v1/eval and v1/invoke endpoints.
"""

__primitive_value_converters = {
    "integer": lambda part: int(part.text),
    "decimal": lambda part: Decimal(part.text),
    "boolean": lambda part: ("False" == part.text),
    "string": lambda part: part.text,
    "map": lambda part: json.loads(part.text),
    "element()": lambda part: part.text,
    "array": lambda part: json.loads(part.text),
    "array-node()": lambda part: json.loads(part.text),
    "object-node()": lambda part: __process_object_node_part(part),
    "document-node()": lambda part: __process_document_node_part(part),
    # It appears that binary() will only be returned for a binary node retrieved
    # from the database, and thus an X-URI will always exist. Have not found a
    # scenario that indicates otherwise.
    "binary()": lambda part: Document(__get_decoded_uri_from_part(part), part.content),
}


def process_multipart_mixed_response(response: Response) -> list:
    """
    Process a multipart REST response by putting them in a list and
    transforming each part based on the "X-Primitive" header.

    :param response: The original multipart/mixed response from a call to a
    MarkLogic server.
    """

    # The presence of this header indicates that the call returned an empty sequence.
    if "Content-Length" in response.headers:
        return []

    parts = MultipartDecoder.from_response(response).parts
    transformed_parts = []
    for part in parts:
        encoding = part.encoding
        header = part.headers["X-Primitive".encode(encoding)].decode(encoding)
        primitive_function = __primitive_value_converters.get(header)
        if primitive_function is not None:
            transformed_parts.append(primitive_function(part))
        else:
            # Return the binary created by requests_toolbelt so we don't get an
            # error trying to convert it to something else.
            transformed_parts.append(part.content)
    return transformed_parts


def __get_decoded_uri_from_part(part):
    encoding = part.encoding
    return part.headers["X-URI".encode(encoding)].decode(encoding)


def __process_object_node_part(part):
    if b"X-URI" in part.headers:
        return Document(__get_decoded_uri_from_part(part), json.loads(part.text))
    else:
        return json.loads(part.text)


def __process_document_node_part(part):
    if b"X-URI" in part.headers:
        return Document(__get_decoded_uri_from_part(part), part.text)
    else:
        return part.text
