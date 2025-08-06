# Copyright (c) 2023-2025 Progress Software Corporation and/or its subsidiaries or affiliates. All Rights Reserved.

from requests import Response


def response_has_no_content(response: Response) -> bool:
    return response.headers.get("Content-Length") == "0"
