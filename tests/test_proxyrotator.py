import pytest

from saferequests.datamodels import Anonymity
from saferequests.proxyrotator import ProxyRotator, is_ipv4_address


@pytest.fixture
def rotator() -> ProxyRotator:
    return ProxyRotator(anonymity=Anonymity.high, livecheck=False, maxshape=10)


def test_is_ipv4_address():
    assert is_ipv4_address("192.168.1.1")
    assert not is_ipv4_address("2001:0db8:85a3:0000:0000:8a2e:0370:7334")
