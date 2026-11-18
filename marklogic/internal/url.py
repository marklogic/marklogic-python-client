# Copyright (c) 2023-2026 Progress Software Corporation and/or its subsidiaries or affiliates. All Rights Reserved.


from urllib.parse import urlsplit


def is_same_origin(url: str, base_url: str) -> bool:
    if not isinstance(url, str) or not isinstance(base_url, str):
        return False

    try:
        url_parts = urlsplit(url)
        base_parts = urlsplit(base_url)
        url_port = url_parts.port
        base_port = base_parts.port
    except ValueError:
        return False

    url_scheme = url_parts.scheme.lower()
    base_scheme = base_parts.scheme.lower()
    url_host = url_parts.hostname
    base_host = base_parts.hostname

    if not url_scheme or not base_scheme or not url_host or not base_host:
        return False

    default_ports = {"http": 80, "https": 443}
    if url_port is None:
        url_port = default_ports.get(url_scheme)
    if base_port is None:
        base_port = default_ports.get(base_scheme)

    url_origin = (url_scheme, url_host.lower(), url_port)
    base_origin = (base_scheme, base_host.lower(), base_port)
    return url_origin == base_origin
