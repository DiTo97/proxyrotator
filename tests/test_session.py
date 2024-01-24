from proxyrotator import ProxiedSession, ProxyRotator


def test_proxiedsession_request_with_rotated_proxy():
    proxy_rotator = ProxyRotator()
    session = ProxiedSession(proxy_rotator=proxy_rotator)

    # Ensure that the request does not raise an exception
    response = session.get("https://www.example.com")
    assert response.status_code == 200

    # Ensure that the current proxy in the session is not None
    assert session.current_proxy is not None


def test_proxiedsession_request_with_404_error():
    proxy_rotator = ProxyRotator()
    session = ProxiedSession(proxy_rotator=proxy_rotator)

    # Ensure that the request raises an exception for a 404 error
    with pytest.raises(requests.exceptions.HTTPError) as e_info:
        session.get("https://www.example.com/404")

    assert e_info.value.response.status_code == 404


def test_proxiedsession_request_with_non_404_error():
    proxy_rotator = ProxyRotator()
    session = ProxiedSession(proxy_rotator=proxy_rotator)

    # Ensure that the request retries with the same proxy for a non-404 error
    with pytest.raises(requests.exceptions.RequestException):
        session.get("https://www.example.com/nonexistent")

    # Ensure that the current proxy in the session is still the same
    assert session.current_proxy is not None
