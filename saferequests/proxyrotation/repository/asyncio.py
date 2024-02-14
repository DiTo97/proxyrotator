import asyncio
import platform
from functools import reduce

import aiohttp
import aiostream
from bs4 import BeautifulSoup as BS

from saferequests.datamodels import Anonymity, Proxy
from saferequests.proxyrotation.repository import (
    URL_freesources,
    URL_sanity,
    abc_Repository,
)


# https://github.com/MagicStack/uvloop/issues/14
if platform.system().lower() != "windows":
    import uvloop

    #
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


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


async def _is_address_reachable(session: aiohttp.ClientSession, address: Proxy) -> bool:
    """If a proxy address is reachable"""
    try:
        async with session.get(
            URL_sanity,
            proxy=f"http://{address}",
            allow_redirects=False,
            timeout=3.0,
        ) as response:
            return response.status == 200
    except (aiohttp.ClientError, asyncio.TimeoutError):
        return False


class Repository(abc_Repository):
    def batch_download(self) -> set[Proxy]:
        return asyncio.run(self._batch_download())

    def reachability(self, available: set[Proxy]) -> tuple[set[Proxy], set[Proxy]]:
        return asyncio.run(self._reachability(available))

    async def _batch_download(self) -> set[Proxy]:
        timeout = aiohttp.ClientTimeout(sock_connect=1.0, sock_read=10.0)

        async with aiohttp.ClientSession(timeout=timeout) as session:
            available = await asyncio.gather(
                *[_batch_download(session, endpoint) for endpoint in URL_freesources]
            )

        available = reduce(lambda x, y: x | y, available)
        return available

    async def _reachability(self, available: set[Proxy]) -> tuple[set[Proxy], set[Proxy]]:
        timeout = aiohttp.ClientTimeout(sock_connect=10.0, sock_read=1.0)

        positive = set()
        negative = set()

        batchsize = self._batchsize if self._batchsize > 0 else len(available)
        batchsize = min(batchsize, len(available))

        async with aiohttp.ClientSession(timeout=timeout) as session:
            iterator = aiostream.stream.iterate(available)
            iterator = aiostream.stream.chunks(iterator, batchsize)

            async with iterator.stream() as chunkset:
                async for batchset in chunkset:
                    response = await asyncio.gather(
                        *[_is_address_reachable(session, address) for address in batchset]
                    )

                    for x in zip(response, batchset):
                        positive.add(x[1]) if x[0] else negative.add(x[1])

        return positive, negative
