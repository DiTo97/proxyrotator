import pytest

from proxyrotator import ProxyRotator


def test_proxyrotator_rotate_with_filters(caplog):
    proxy_rotator = ProxyRotator(
        anonymity="anonymous", secure=True, country_codes_alpha2={"US", "CA"}
    )

    with caplog.at_level(logging.WARNING):
        proxy_rotator.rotate()

    assert "No freezies are available at the moment." in caplog.text


def test_proxyrotator_rotate_with_valid_proxy():
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        proxy_rotator = ProxyRotator(
            cache=temp_file.name, max_num_proxies=5, t_refresh=60
        )

        assert os.path.getsize(temp_file.name) == 0

        proxy_rotator.rotate()

        assert os.path.getsize(temp_file.name) > 0
        assert proxy_rotator.selected in proxy_rotator.proxy_df["URL"].astype(
            str
        ).str.cat(proxy_rotator.proxy_df["port"].astype(str), sep=":")

    os.remove(temp_file.name)


def test_proxyrotator_rotate_without_filters():
    proxy_rotator = ProxyRotator()

    # Ensure that the rotation does not raise an exception
    proxy_rotator.rotate()

    # Ensure that the selected proxy is in the available set
    assert proxy_rotator.selected in proxy_rotator.proxy_df["URL"].astype(str).str.cat(
        proxy_rotator.proxy_df["port"].astype(str), sep=":"
    )


def test_proxyrotator_rotate_with_anonymity_filter():
    proxy_rotator = ProxyRotator(anonymity="elite")

    # Ensure that the rotation does not raise an exception
    proxy_rotator.rotate()

    # Ensure that the selected proxy has the specified anonymity level
    assert proxy_rotator.proxy_df["anonymity"].iloc[0] == "elite"


def test_proxyrotator_rotate_with_secure_filter():
    proxy_rotator = ProxyRotator(secure=False)

    # Ensure that the rotation does not raise an exception
    proxy_rotator.rotate()

    # Ensure that the selected proxy does not require HTTPS support
    assert proxy_rotator.proxy_df["secure"].iloc[0] is False


def test_proxyrotator_rotate_with_country_code_filter():
    proxy_rotator = ProxyRotator(country_codes_alpha2={"US"})

    # Ensure that the rotation does not raise an exception
    proxy_rotator.rotate()

    # Ensure that the selected proxy is from the specified country
    assert proxy_rotator.proxy_df["alpha2_code"].iloc[0] == "us"


def test_proxyrotator_rotate_without_available_proxies():
    proxy_rotator = ProxyRotator(max_num_proxies=5)

    # Ensure that the rotation does not raise an exception
    proxy_rotator.rotate()

    # Ensure that the selected proxy is None as no proxies are available
    assert proxy_rotator.selected is None


def test_proxyrotator_rotate_with_disabled_refresh():
    proxy_rotator = ProxyRotator(t_refresh=-1, max_num_proxies=5)

    # Ensure that the rotation does not raise an exception
    proxy_rotator.rotate()

    # Ensure that the selected proxy is in the available set
    assert proxy_rotator.selected in proxy_rotator.proxy_df["URL"].astype(str).str.cat(
        proxy_rotator.proxy_df["port"].astype(str), sep=":"
    )


def test_proxyrotator_rotate_with_blocked_proxies():
    proxy_rotator = ProxyRotator(max_num_proxies=5)

    # Manually add a proxy to the blocked set
    blocked_proxy = "example.com:8080"
    proxy_rotator._blocked.add(blocked_proxy)

    # Ensure that the rotation does not select a blocked proxy
    proxy_rotator.rotate()
    assert proxy_rotator.selected is not None
    assert proxy_rotator.selected != blocked_proxy


def test_proxyrotator_cache_loading_and_saving():
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        proxy_rotator = ProxyRotator(cache=temp_file.name)

        # Simulate a rotation to add data to the cache
        proxy_rotator.rotate()

        # Ensure that the cache file is not empty
        assert os.path.getsize(temp_file.name) > 0

        # Save the current state
        initial_cache_size = os.path.getsize(temp_file.name)

        # Perform another rotation to update the cache
        proxy_rotator.rotate()

        # Ensure that the cache file size has increased
        assert os.path.getsize(temp_file.name) > initial_cache_size

    os.remove(temp_file.name)
