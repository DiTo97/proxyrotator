# your_module_name.py

import asyncio
import ipaddress
import json
import logging
import random
import typing
from datetime import datetime, timedelta

import aiohttp
import pandas as pd
import requests
from bs4 import BeautifulSoup as BS


class ProxyRotator:
    _URL_freexies = ["https://sslproxies.org/", "https://free-proxy-list.net/"]

    CSV_FILENAME = "proxies.csv"
    URL_TO_CHECK = "https://ip.oxylabs.io/ip"
    TIMEOUT_IN_SECONDS = 10

    def __init__(
        self,
        *,
        anonymity: typing.Optional[str] = None,
        secure: bool = True,
        country_codes_alpha2: typing.Optional[typing.Set[str]] = None,
        max_num_proxies: int = -1,
        verbose: bool = False,
        t_refresh: int = -1,
        cache: typing.Optional[str] = None,
        livecheck: bool = False,  # New parameter for live checking
    ):
        self._blocked = set()
        self._secure = secure
        self._anonymity = anonymity
        self._country_codes_alpha2 = country_codes_alpha2
        self._max_num_proxies = max_num_proxies
        self._selected = None
        self._verbose = verbose
        self._logger = self._configure_logger()
        self._proxy_df = pd.DataFrame(
            columns=["URL", "port", "alpha2_code", "anonymity", "secure"]
        )
        self._last_download_time = None
        self._cache = cache
        self._livecheck = livecheck  # New attribute for live checking
        self._load_from_cache()

    def _configure_logger(self) -> logging.Logger:
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.WARNING)
        ch = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        return logger

    def _load_from_cache(self) -> None:
        if self._cache is not None:
            try:
                with open(self._cache, "r") as file:
                    cache_data = json.load(file)
                    self._proxy_df = pd.DataFrame(cache_data.get("proxy_data", []))
            except (FileNotFoundError, json.JSONDecodeError):
                pass

    def _save_to_cache(self) -> None:
        if self._cache is not None:
            cache_data = {"proxy_data": self._proxy_df.to_dict(orient="records")}
            with open(self._cache, "w") as file:
                json.dump(cache_data, file)

    def _t_refresh_enabled(self) -> bool:
        return self._t_refresh > 0

    def _time_to_refresh(self) -> bool:
        if self._last_download_time is None:
            return True

        elapsed_time = datetime.now() - self._last_download_time
        return elapsed_time.total_seconds() > self._t_refresh

    async def check_proxy(self, proxy: str) -> bool:
        try:
            session_timeout = aiohttp.ClientTimeout(
                total=None,
                sock_connect=self.TIMEOUT_IN_SECONDS,
                sock_read=self.TIMEOUT_IN_SECONDS,
            )
            async with aiohttp.ClientSession(timeout=session_timeout) as session:
                async with session.get(
                    self.URL_TO_CHECK,
                    proxy=f"http://{proxy}",
                    timeout=self.TIMEOUT_IN_SECONDS,
                ) as resp:
                    return resp.status == 200
        except Exception as error:
            self._logger.warning("Proxy %s responded with an error: %s", proxy, error)
            return False

    async def livecheck_proxies(self) -> None:
        tasks = [
            self.check_proxy(row["URL"] + ":" + str(row["port"]))
            for index, row in self._proxy_df.iterrows()
        ]
        results = await asyncio.gather(*tasks)

        for result, (_, row) in zip(results, self._proxy_df.iterrows()):
            if not result:
                proxy = f"{row['URL']}:{row['port']}"
                self._logger.warning("Removing invalid proxy: %s", proxy)
                self._blocked.add(proxy)

    async def _download_and_pop(self) -> None:
        if self.num_available == 0:
            self._download()

        if self.num_available == 0:
            self._selected = None
            return

        if self._livecheck:
            await self.livecheck_proxies()

        self._apply_filters()
        selected_row = self._proxy_df.sample(1).iloc[0]
        self._selected = f"{selected_row['URL']}:{selected_row['port']}"

    def rotate(self) -> None:
        if self._selected is not None:
            self._blocked.add(self._selected)

        if self._t_refresh_enabled() and self._time_to_refresh():
            self._download()

        self._download_and_pop()
        self._save_to_cache()

    async def _download(self):
        if self._max_num_proxies == 0:
            return

        if self._verbose:
            message = "Downloading proxies..."
            print(message)

        self._proxy_df = pd.DataFrame(
            columns=["URL", "port", "alpha2_code", "anonymity", "secure"]
        )

        async with aiohttp.ClientSession() as session:
            # Create a list to store tasks for each URL
            tasks = [
                self._download_url(session, endpoint) for endpoint in self._URL_freexies
            ]

            # Gather all tasks to execute concurrently
            await asyncio.gather(*tasks)

        # Remove blocked proxies
        self._proxy_df = self._proxy_df[
            ~self._proxy_df["URL"]
            .astype(str)
            .str.cat(self._proxy_df["port"].astype(str), sep=":")
            .isin(self._blocked)
        ]

        abundance = self.num_available > self._max_num_proxies

        if abundance and self._max_num_proxies > -1:
            self._proxy_df = self._proxy_df.sample(n=self._max_num_proxies)

        self._last_download_time = datetime.now()

    async def _download_url(self, session, endpoint):
        response = await session.get(endpoint)
        soup = BS(response.content, "html5lib")

        addresses = soup.findAll("td")[::8]
        ports = soup.findAll("td")[1::8]
        country_codes = soup.findAll("td")[2::8]  # Placeholder for country codes
        anonymities = soup.findAll("td")[4::8]
        supports_https = soup.findAll("td")[6::8]

        available = list(
            zip(
                map(lambda x: x.text.lower(), addresses),
                map(lambda x: x.text.lower(), ports),
                map(lambda x: x.text.lower(), country_codes),
                map(lambda x: x.text.lower(), anonymities),
                map(lambda x: x.text.lower(), supports_https),
            )
        )

        available = [
            {
                "URL": address,
                "port": int(port),
                "alpha2_code": alpha2_code.upper(),  # Assuming country codes are uppercased
                "anonymity": anonymity,
                "secure": https_support == "yes",
            }
            for address, port, alpha2_code, anonymity, https_support in available
            if self._is_valid_proxy(address, anonymity, https_support)
        ]

        # Append to the DataFrame in a thread-safe manner
        async with self._proxy_df_lock:
            self._proxy_df = self._proxy_df.append(available, ignore_index=True)

    def _apply_filters(self) -> None:
        if self._country_codes_alpha2:
            self._proxy_df = self._proxy_df[
                self._proxy_df["alpha2_code"].isin(self._country_codes_alpha2)
            ]

        if self._anonymity:
            self._proxy_df = self._proxy_df[
                self._proxy_df["anonymity"] == self._anonymity
            ]

        if self._secure is not None:
            self._proxy_df = self._proxy_df[self._proxy_df["secure"] == self._secure]

    # ... Existing methods remain the same ...

    @property
    def proxy_df(self) -> pd.DataFrame:
        return self._proxy_df

    @property
    def num_available(self) -> int:
        return len(self._proxy_df)

    @property
    def selected(self) -> str:
        return self._selected
