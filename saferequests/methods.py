from typing import Any

import requests

from saferequests import sessions


def request(
    method: str, endpoint: str, max_rotations: int = 5, **kwargs: Any
) -> requests.Response:
    """It sends a HTTP request with the given method"""
    with sessions.Session() as session:
        return session.request(method, endpoint, max_rotations=max_rotations, **kwargs)


def get(
    endpoint: str, max_rotations: int = 5, params: Any | None = None, **kwargs: Any
) -> requests.Response:
    """It sends a GET request"""
    return request(
        "get", endpoint, max_rotations=max_rotations, params=params, **kwargs
    )


def options(endpoint: str, max_rotations: int = 5, **kwargs: Any) -> requests.Response:
    """It sends a OPTIONS request"""
    return request("options", endpoint, max_rotations=max_rotations, **kwargs)


def head(endpoint: str, max_rotations: int = 5, **kwargs: Any) -> requests.Response:
    """It sends a HEAD request"""
    kwargs.setdefault("allow_redirects", False)
    return request("head", endpoint, max_rotations=max_rotations, **kwargs)


def post(
    endpoint: str,
    max_rotations: int = 5,
    data: Any | None = None,
    **kwargs: Any,
) -> requests.Response:
    """It sends a POST request"""
    return request("post", endpoint, max_rotations=max_rotations, data=data, **kwargs)


def put(
    endpoint: str,
    max_rotations: int = 5,
    data: Any | None = None,
    **kwargs: Any,
) -> requests.Response:
    """It sends a PUT request"""
    return request("put", endpoint, max_rotations=max_rotations, data=data, **kwargs)


def patch(
    endpoint: str,
    max_rotations: int = 5,
    data: Any | None = None,
    **kwargs: Any,
) -> requests.Response:
    """It sends a PATCH request"""
    return request("patch", endpoint, max_rotations=max_rotations, data=data, **kwargs)


def delete(endpoint: str, max_rotations: int = 5, **kwargs: Any) -> requests.Response:
    """It sends a DELETE request"""
    return request("delete", endpoint, max_rotations=max_rotations, **kwargs)
