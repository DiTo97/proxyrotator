# import asyncio
# from unittest.mock import patch

# import aiohttp
# import pytest

# from saferequests.datamodels import Anonymity, Proxy
# from saferequests.proxyrotator import (
#     ProxyRotator,
#     _batch_download,
#     is_ipv4_address,
#     is_reachable_address,
# )


# @pytest.fixture
# def rotator() -> ProxyRotator:
#     return ProxyRotator(anonymity=Anonymity.high, livecheck=False, maxshape=10)


# def test_is_ipv4_address():
#     assert is_ipv4_address("192.168.1.1")
#     assert not is_ipv4_address("2001:0db8:85a3:0000:0000:8a2e:0370:7334")


# @patch("aiohttp.ClientSession.get")
# async def test_is_reachable_address(mock_get):
#     mock_get.return_value.__aenter__.return_value.status = 200
#     assert await is_reachable_address(
#         aiohttp.ClientSession(),
#         Proxy("192.168.1.1", 8080, "US", Anonymity.high, True),
#     )


# @patch("aiohttp.ClientSession.get")
# async def test_batch_download(mock_get):
#     mock_get.return_value.__aenter__.return_value.status = 200
#     assert isinstance(
#         await _batch_download(aiohttp.ClientSession(), "https://sslproxies.org/"), set
#     )


# def test_proxy_rotator():
#     rotator = ProxyRotator()
#     assert len(rotator) == 0
#     assert rotator.crawledset == set()
#     assert rotator.selected is None


# @patch("saferequests.proxyrotator._batch_download")
# @patch("saferequests.proxyrotator.is_reachable_address")
# def test_proxy_rotator_rotate(mock_is_reachable_address, mock_batch_download):
#     mock_is_reachable_address.return_value = asyncio.Future()
#     mock_is_reachable_address.return_value.set_result(True)
#     mock_batch_download.return_value = asyncio.Future()
#     mock_batch_download.return_value.set_result(
#         set([Proxy("192.168.1.1", 8080, "US", Anonymity.high, True)])
#     )
#     rotator = ProxyRotator()
#     rotator.rotate()
#     assert len(rotator) > 0
#     assert rotator.selected is not None


# def test_proxy_rotator_properties():
#     rotator = ProxyRotator()
#     assert rotator.crawledset == set()
#     assert rotator.selected is None


# @patch("saferequests.proxyrotator._batch_download")
# @patch("saferequests.proxyrotator.is_reachable_address")
# def test_proxy_rotator_rotate_no_proxies(
#     mock_is_reachable_address, mock_batch_download
# ):
#     mock_is_reachable_address.return_value = asyncio.Future()
#     mock_is_reachable_address.return_value.set_result(True)
#     mock_batch_download.return_value = asyncio.Future()
#     mock_batch_download.return_value.set_result(set())
#     rotator = ProxyRotator()
#     rotator.rotate()
#     assert len(rotator) == 0
#     assert rotator.selected is None


# @patch("saferequests.proxyrotator._batch_download")
# @patch("saferequests.proxyrotator.is_reachable_address")
# def test_proxy_rotator_rotate_blocked_proxies(
#     mock_is_reachable_address, mock_batch_download
# ):
#     mock_is_reachable_address.return_value = asyncio.Future()
#     mock_is_reachable_address.return_value.set_result(False)
#     mock_batch_download.return_value = asyncio.Future()
#     mock_batch_download.return_value.set_result(
#         set([Proxy("192.168.1.1", 8080, "US", Anonymity.high, True)])
#     )
#     rotator = ProxyRotator()
#     rotator.rotate()
#     assert len(rotator) == 0
#     assert rotator.selected is None


# # ... existing tests ...


# @patch("saferequests.proxyrotator._batch_download")
# @patch("saferequests.proxyrotator.is_reachable_address")
# def test_proxy_rotator_rotate_with_schedule(
#     mock_is_reachable_address, mock_batch_download
# ):
#     mock_is_reachable_address.return_value = asyncio.Future()
#     mock_is_reachable_address.return_value.set_result(True)
#     mock_batch_download.return_value = asyncio.Future()
#     proxies = set(
#         [Proxy(f"192.168.1.{i}", 8080, "US", Anonymity.high, True) for i in range(20)]
#     )
#     mock_batch_download.return_value.set_result(proxies)
#     rotator = ProxyRotator(schedule=60.0)
#     rotator.rotate()
#     assert rotator._downloaded is not None


# @patch("saferequests.proxyrotator._batch_download")
# @patch("saferequests.proxyrotator.is_reachable_address")
# def test_proxy_rotator_rotate_with_livecheck(
#     mock_is_reachable_address, mock_batch_download
# ):
#     mock_is_reachable_address.return_value = asyncio.Future()
#     mock_is_reachable_address.return_value.set_result(False)
#     mock_batch_download.return_value = asyncio.Future()
#     proxies = set(
#         [Proxy(f"192.168.1.{i}", 8080, "US", Anonymity.high, True) for i in range(20)]
#     )
#     mock_batch_download.return_value.set_result(proxies)
#     rotator = ProxyRotator(livecheck=True)
#     rotator.rotate()
#     assert len(rotator) == 0
#     assert rotator.selected is None


# # ... existing tests ...


# def test_proxy_rotator_with_cachedir(tmp_path):
#     d = tmp_path / "sub"
#     d.mkdir()
#     rotator = ProxyRotator(cachedir=str(d))
#     assert rotator._cachedir == d
#     rotator.rotate()
#     assert (d / "saferequests.pkl").exists()


# def test_proxy_rotator_from_cachedir(tmp_path):
#     d = tmp_path / "sub"
#     d.mkdir()
#     rotator1 = ProxyRotator(cachedir=str(d))
#     rotator1.rotate()
#     rotator2 = ProxyRotator(cachedir=str(d))
#     assert rotator1._crawledset == rotator2._crawledset
#     assert rotator1._selected == rotator2._selected


# @patch("saferequests.proxyrotator._batch_download")
# @patch("saferequests.proxyrotator.is_reachable_address")
# def test_proxy_rotator_rotate_with_livecheck_and_cachedir(
#     mock_is_reachable_address, mock_batch_download, tmp_path
# ):
#     d = tmp_path / "sub"
#     d.mkdir()
#     mock_is_reachable_address.return_value = asyncio.Future()
#     mock_is_reachable_address.return_value.set_result(False)
#     mock_batch_download.return_value = asyncio.Future()
#     proxies = set(
#         [Proxy(f"192.168.1.{i}", 8080, "US", Anonymity.high, True) for i in range(20)]
#     )
#     mock_batch_download.return_value.set_result(proxies)
#     rotator = ProxyRotator(livecheck=True, cachedir=str(d))
#     rotator.rotate()
#     assert len(rotator) == 0
#     assert rotator.selected is None
#     assert (d / "saferequests.pkl").exists()
