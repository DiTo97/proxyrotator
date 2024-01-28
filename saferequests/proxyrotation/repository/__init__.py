import importlib
from abc import ABC, abstractmethod
from typing import Any

from saferequests.datamodels import Proxy


URL_freesources = ["https://sslproxies.org", "https://free-proxy-list.net"]
URL_sanity = "https://ip.oxylabs.io"


class abc_Repository(ABC):
    @abstractmethod
    def batch_download(self) -> set[Proxy]:
        """It downloads a batch of proxy addresses from free public sources

        Returns:
            A set of unique proxy addresses that were successfully downloaded.
        """

    @abstractmethod
    def reachability(
        self, available: set[Proxy], batchsize: int = 0
    ) -> tuple[set[Proxy], set[Proxy]]:
        """
        Check the availability of a given set of proxies.

        Args:
            available (set[Proxy]): A set of proxy addresses to check.

        Returns:
            tuple[set[Proxy], set[Proxy]]: A tuple containing two sets:
                - The first set contains proxies that are still alive.
                - The second set contains proxies that are not alive.
        """


def from_name(repository: str, *args: Any, **kwargs: Any) -> abc_Repository:
    module = f"saferequests.proxyrotation.repository._{repository}"
    module = importlib.import_module(module)

    instance = module.Repository(*args, **kwargs)
    return instance
