from requests import Response


def response_has_no_content(response: Response) -> bool:
    return response.headers.get("Content-Length") == "0"
