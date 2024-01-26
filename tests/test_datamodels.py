from dataclasses import asdict

import pytest

from saferequests.datamodels import Anonymity, Proxy


@pytest.fixture
def address() -> Proxy:
    return Proxy("192.168.1.1", 8080, "US", Anonymity.high, True)


def test_anonymity_from_string():
    assert Anonymity.from_string("elite proxy") == Anonymity.high
    assert Anonymity.from_string("anonymous") == Anonymity.medium
    assert Anonymity.from_string("transparent") == Anonymity.weak
    assert Anonymity.from_string("unknown") == Anonymity.unknown
    assert Anonymity.from_string("a1b2c3d4e5") == Anonymity.unknown


def test_proxy_asdict(address: Proxy):
    assert asdict(address) == {
        "address": "192.168.1.1",
        "port": 8080,
        "country": "US",
        "anonymity": "elite proxy",
        "secure": True,
    }


def test_proxy_hash_matching(address: Proxy):
    forward = Proxy("192.168.1.1", 8080, "EU", Anonymity.medium, False)
    assert hash(address) == hash(forward)


def test_proxy_hash_nonmatching(address: Proxy):
    forward = Proxy("192.168.1.1", 8081, "US", Anonymity.medium, False)
    assert hash(address) != hash(forward)


def test_proxy_str(address: Proxy):
    assert str(address) == "192.168.1.1:8080"
