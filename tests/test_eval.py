from requests_toolbelt.multipart.decoder import MultipartDecoder


def test_eval(client):
    """
    This shows how a user would do an eval today. It's a good example of how a multipart/mixed
    response is a little annoying to deal with, as it requires using the requests_toolbelt
    library and a class called MultipartDecoder.

    Client support for this might look like this:
    response = client.eval.xquery("<hello>world</hello>")

    And then it's debatable whether we want to do anything beyond what MultipartDecoder
    is doing for handling the response.
    """
    response = client.post(
        "v1/eval",
        headers={"Content-type": "application/x-www-form-urlencoded"},
        data={"xquery": "<hello>world</hello>"},
    )

    decoder = MultipartDecoder.from_response(response)
    content = decoder.parts[0].text
    assert "<hello>world</hello>" == content
