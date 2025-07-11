import math
import ast
from marklogic.vectors import VectorUtil
from marklogic import Client

VECTOR = [3.14, 1.59, 2.65]
EXPECTED_BASE64 = "AAAAAAMAAADD9UhAH4XLP5qZKUA="
ACCEPTABLE_DELTA = 0.0001


def test_encode_and_decode_with_python():
    encoded = VectorUtil.base64_encode(VECTOR)
    assert encoded == EXPECTED_BASE64

    decoded = VectorUtil.base64_decode(encoded)
    assert len(decoded) == len(VECTOR)
    for a, b in zip(decoded, VECTOR):
        assert abs(a - b) < ACCEPTABLE_DELTA


def test_decode_known_base64():
    decoded = VectorUtil.base64_decode(EXPECTED_BASE64)
    assert len(decoded) == len(VECTOR)
    for a, b in zip(decoded, VECTOR):
        assert abs(a - b) < ACCEPTABLE_DELTA


def test_encode_and_decode_with_server(client: Client):
    """
    Encode a vector in Python, decode it on the MarkLogic server, and check the result.
    """
    encoded = VectorUtil.base64_encode(VECTOR)
    assert encoded == EXPECTED_BASE64

    # Use MarkLogic's eval endpoint to decode the vector on the server
    xquery = f"vec:base64-decode('{encoded}')"
    binary_result = client.eval(xquery=xquery)
    float_list = ast.literal_eval(binary_result[0].decode("utf-8"))
    assert len(float_list) == len(VECTOR)
    for a, b in zip(float_list, VECTOR):
        assert math.isclose(a, b, abs_tol=ACCEPTABLE_DELTA)


def test_encode_with_server_and_decode_with_python(client: Client):
    """
    Encode a vector on the MarkLogic server, decode it in Python, and check the result.
    """
    xquery = "vec:base64-encode(vec:vector((3.14, 1.59, 2.65)))"
    encoded = client.eval(xquery=xquery)[0]
    assert encoded == EXPECTED_BASE64

    decoded = VectorUtil.base64_decode(encoded)
    assert len(decoded) == len(VECTOR)
    for a, b in zip(decoded, VECTOR):
        assert math.isclose(a, b, abs_tol=ACCEPTABLE_DELTA)
