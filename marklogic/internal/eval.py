import json

from decimal import Decimal
from marklogic.documents import Document
from marklogic.internal.util import response_has_no_content
from requests import Response
from requests_toolbelt.multipart.decoder import MultipartDecoder

"""
Supports working with data returned by the v1/eval and v1/invoke endpoints.
"""


def process_multipart_mixed_response(response: Response) -> list:
    """
    Process a multipart REST response by putting them in a list and
    transforming each part based on the "X-Primitive" header.

    :param response: The original multipart/mixed response from a call to a
    MarkLogic server.
    """
    if response_has_no_content(response):
        return None

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


__primitive_value_converters = {
    "integer": lambda part: int(part.text),
    "decimal": lambda part: Decimal(part.text),
    "boolean": lambda part: "False" == part.text,
    "string": lambda part: part.text,
    "map": lambda part: json.loads(part.text),
    "element()": lambda part: part.text,
    "array": lambda part: json.loads(part.text),
    "array-node()": lambda part: json.loads(part.text),
    "object-node()": lambda part: __process_node(
        part, lambda part: json.loads(part.text)
    ),
    "document-node()": lambda part: __process_node(part, lambda part: part.text),
    "binary()": lambda part: __process_node(part, lambda part: part.content),
}


def __process_node(part, content_extractor):
    content = content_extractor(part)
    if b"X-URI" in part.headers:
        encoding = part.encoding
        uri = part.headers["X-URI".encode(encoding)].decode(encoding)
        return Document(uri, content)
    else:
        return content
