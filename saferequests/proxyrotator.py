import asyncio
import ipaddress
import pathlib
import pickle
import platform
import random
from datetime import datetime
from functools import reduce

import aiohttp
import aiostream
from bs4 import BeautifulSoup as BS

from saferequests.datamodels import Anonymity, Proxy


# https://github.com/MagicStack/uvloop/issues/14
if platform.system().lower() != "windows":
    import uvloop

    #
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


_URL_freesources = ["https://sslproxies.org/", "https://free-proxy-list.net/"]
_URL_sanity = "https://ip.oxylabs.io/ip"


def is_ipv4_address(address: str | Proxy) -> bool:
    """If a proxy address conforms to a IPv4 address"""
    if isinstance(address, Proxy):
        address = address.address

    try:
        ipaddress.IPv4Address(address)
        return True
    except ipaddress.AddressValueError:
        return False


async def is_reachable_address(session: aiohttp.ClientSession, address: Proxy) -> bool:
    """If a proxy address is reachable"""
    try:
        async with session.get(
            _URL_sanity, proxy=f"http://{address}", allow_redirects=False, timeout=1.0
        ) as response:
            return response.status == 200
    except asyncio.TimeoutError:
        return False


async def _batch_download(session: aiohttp.ClientSession, endpoint: str) -> set[Proxy]:
    """It downloads a batch of proxy addresses from a free public source"""
    async with session.get(endpoint) as response:
        if response.status != 200:
            return set()

        response = await response.text()

    soup = BS(response, "html5lib")

    available = zip(
        map(lambda x: x.text.lower(), soup.findAll("td")[::8]),
        map(lambda x: x.text.lower(), soup.findAll("td")[1::8]),
        map(lambda x: x.text.upper(), soup.findAll("td")[2::8]),
        map(lambda x: x.text.lower(), soup.findAll("td")[4::8]),
        map(lambda x: x.text.lower(), soup.findAll("td")[6::8]),
    )

    available = set(
        Proxy(
            address=address,
            port=port,
            country=country,
            anonymity=Anonymity.from_string(anonymity),
            secure=secure == "yes",
        )
        for address, port, country, anonymity, secure in available
    )

    return available


class ProxyRotator:
    """A class that automatically rotates proxy addresses for HTTP requests

    It allows specifying various filters, such as anonymity level, connection
    security, ISO 3166-1 alpha-2 country code, and downloading from free public sources,
    while ensuring the sanity of any proxy address retrieved.
    """

    _anonymity: Anonymity | None
    _blockedset: set[Proxy]
    _cachedir: pathlib.Path | None
    _countryset: set[str] | None
    _downloaded: datetime | None
    _livecheck: bool
    _maxshape: int
    _crawledset: set[Proxy]
    _schedule: float
    _secure: bool
    _selected: Proxy | None

    def __init__(
        self,
        *,
        anonymity: Anonymity | None = None,
        cachedir: str | None = None,
        countryset: set[str] | None = None,
        livecheck: bool = False,
        maxshape: int = 0,
        schedule: float = 0.0,
        secure: bool = True,
    ):
        self._anonymity = anonymity
        self._blockedset = set()
        self._cachedir = None
        self._countryset = countryset
        self._downloaded = None
        self._livecheck = livecheck
        self._maxshape = maxshape
        self._crawledset = set()
        self._schedule = schedule
        self._secure = secure
        self._selected = None

        if cachedir:
            self._cachedir = pathlib.Path(cachedir).expanduser().resolve()

        self._from_cachedir()

    def __len__(self) -> int:
        """The number of crawled proxy addresses"""
        return len(self._crawledset)

    @property
    def crawledset(self) -> set[Proxy]:
        """The set of crawled proxy addresses"""
        return self._crawledset

    @property
    def selected(self) -> Proxy | None:
        """The selected proxy address"""
        return self._selected

    def rotate(self) -> None:
        """It rotates blocking the selected proxy address"""
        if self._selected is not None:
            self._blockedset.add(self._selected)
            self._selected = None

        if self._should_download():
            asyncio.run(self._download())

        if len(self._crawledset) > 0:
            self._selected = self._crawledset.pop()

        self._to_cachedir()

    def _from_cachedir(self) -> None:
        """It loads the rotator state from the cache dir"""
        if not self._cachedir:
            return

        cacheset = self._cachedir / "snapshot.pickle"

        if not cacheset.exists():
            return

        with cacheset.open("rb") as f:
            snapshot = pickle.load(f)

        assert (
            self._anonymity == snapshot["anonymity"]
        ), "The anonymity level has changed"
        assert self._secure == snapshot["secure"], "The security protocol has changed"

        self._blockedset = snapshot["blockedset"]
        self._crawledset = snapshot["crawledset"]
        self._selected = snapshot["selected"]

    def _should_download(self) -> bool:
        """If a batch of proxy addressess should be downloaded"""
        if self._schedule > 0.0:
            if self._downloaded is None:
                return True

            elapsed = datetime.now() - self._downloaded
            elapsed = elapsed.total_seconds()

            if elapsed > self._schedule:
                return True

        return len(self._crawledset) == 0

    def _should_keep(self, address: Proxy) -> bool:
        """If a proxy address should be kept after filtering"""
        if not is_ipv4_address(address):
            return False

        if self._anonymity is not None:
            if address.anonymity != self._anonymity:
                return False

        if self._countryset is not None:
            if address.country not in self._countryset:
                return False

        if address.secure != self._secure:
            return False

        return True

    def _to_cachedir(self) -> None:
        """It saves the rotator state to the cache dir"""
        if not self._cachedir:
            return

        if not self._cachedir.exists():
            self._cachedir.mkdir(parents=True)

        cacheset = self._cachedir / "snapshot.pickle"

        snapshot = {
            "anonymity": self._anonymity,
            "blockedset": self._blockedset,
            "crawledset": self._crawledset,
            "secure": self._secure,
            "selected": self._selected,
        }

        with cacheset.open("wb") as f:
            pickle.dump(snapshot, f)

    async def _download(self):
        session_timeout = aiohttp.ClientTimeout(sock_connect=1.0, sock_read=10.0)

        async with aiohttp.ClientSession(timeout=session_timeout) as session:
            available = await asyncio.gather(
                *[_batch_download(session, endpoint) for endpoint in _URL_freesources]
            )

        available = reduce(lambda x, y: x | y, available)
        available = available - self._blockedset
        available = set(filter(self._should_keep, available))

        if self._livecheck:
            session_timeout = aiohttp.ClientTimeout(sock_connect=10.0, sock_read=1.0)

            async with aiohttp.ClientSession(timeout=session_timeout) as session:
                iterator = aiostream.stream.iterate(available)
                iterator = aiostream.stream.chunks(iterator, 10)  # batch size

                async with iterator.stream() as chunkset:
                    async for B in chunkset:
                        reachable = await asyncio.gather(
                            *[is_reachable_address(session, address) for address in B]
                        )

                        for status, address in zip(reachable, B):
                            if not status:
                                available.remove(address)
                                self._blockedset.add(address)

        self._crawledset.update(available)

        if self._maxshape > 0:
            abundance = len(self._crawledset) > self._maxshape

            if abundance:
                self._crawledset = set(random.sample(self._crawledset, self._maxshape))

        self._downloaded = datetime.now()
