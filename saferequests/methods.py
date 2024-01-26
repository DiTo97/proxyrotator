from typing import Any

import requests

from saferequests import sessions


def request(
    method: str, url: str, max_rotations: int = 10, **kwargs: Any
) -> requests.Response:
    """It sends a HTTP request with the given method"""
    with sessions.Session() as session:
        return session.request(method, url, max_rotations=max_rotations, **kwargs)


def get(
    url: str, max_rotations: int = 10, params: Any | None = None, **kwargs: Any
) -> requests.Response:
    """It sends a GET request"""
    return request("get", url, max_rotations=max_rotations, params=params, **kwargs)


def options(url: str, max_rotations: int = 10, **kwargs: Any) -> requests.Response:
    """It sends a OPTIONS request"""
    return request("options", url, max_rotations=max_rotations, **kwargs)


def head(url: str, max_rotations: int = 10, **kwargs: Any) -> requests.Response:
    """It sends a HEAD request"""
    kwargs.setdefault("allow_redirects", False)
    return request("head", url, max_rotations=max_rotations, **kwargs)


def post(
    url: str,
    max_rotations: int = 10,
    data: Any | None = None,
    json: Any | None = None,
    **kwargs: Any,
) -> requests.Response:
    """It sends a POST request"""
    return request(
        "post", url, max_rotations=max_rotations, data=data, json=json, **kwargs
    )


def put(
    url: str,
    max_rotations: int = 10,
    data: Any | None = None,
    **kwargs: Any,
) -> requests.Response:
    """It sends a PUT request"""
    return request("put", url, max_rotations=max_rotations, data=data, **kwargs)


def patch(
    url: str,
    max_rotations: int = 10,
    data: Any | None = None,
    **kwargs: Any,
) -> requests.Response:
    """It sends a PATCH request"""
    return request("patch", url, max_rotations=max_rotations, data=data, **kwargs)


def delete(url: str, max_rotations: int = 10, **kwargs: Any) -> requests.Response:
    """It sends a DELETE request"""
    return request("delete", url, max_rotations=max_rotations, **kwargs)
