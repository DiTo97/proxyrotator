import importlib
from abc import ABC, abstractmethod
from typing import Any

from saferequests.datamodels import Proxy


URL_freesources = ["https://sslproxies.org", "https://free-proxy-list.net"]
URL_sanity = "https://ip.oxylabs.io"


class abc_Repository(ABC):
    _batchsize: int

    def __init__(self, batchsize: int = 10) -> None:
        self._batchsize = batchsize

    @abstractmethod
    def batch_download(self) -> set[Proxy]:
        """It downloads a batch of proxy addresses from free public sources"""

    @abstractmethod
    def reachability(self, available: set[Proxy]) -> tuple[set[Proxy], set[Proxy]]:
        """It separates available proxy addresses into reachable and unreachable"""


def from_name(repository: str, *args: Any, **kwargs: Any) -> abc_Repository:
    """A factory method for repository import"""
    module = f"saferequests.proxyrotation.repository.{repository}"
    module = importlib.import_module(module)

    instance = module.Repository(*args, **kwargs)
    return instance
