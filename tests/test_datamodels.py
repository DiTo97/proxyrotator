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
    assert Anonymity.from_string("invalid") == Anonymity.unknown


def test_proxy_str(address: Proxy):
    assert str(address) == "192.168.1.1:8080"


def test_proxy_dict(address: Proxy):
    assert asdict(address) == {
        "address": "192.168.1.1",
        "port": 8080,
        "country": "US",
        "anonymity": "elite proxy",
        "secure": True,
    }
