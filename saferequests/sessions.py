from typing import Any

import requests

from saferequests.proxyrotator import ProxyRotator


class Session(requests.Session):
    def __init__(
        self,
        *args: Any,
        max_rotations: int = 10,
        rotator: ProxyRotator | None = None,
        **kwargs: Any,
    ):
        super().__init__(*args, **kwargs)

        self._rotator = rotator or ProxyRotator()
        self._max_rotations = max_rotations

    def request(
        self, method: str, url: str, *args: Any, **kwargs: Any
    ) -> requests.Response:
        if not self._rotator.selected:
            self._rotator.rotate()

        for _ in range(self._max_rotations):
            if not self._rotator.selected:
                raise requests.HTTPError("No available proxy addresses")

            address = str(self._rotator.selected)
            kwargs["proxies"] = {"http": address, "https": address}

            response = super().request(method, url, *args, **kwargs)

            if response.status_code != 200:
                self._rotator.rotate()
                continue

            return response

        raise requests.HTTPError("No proxy rotations left")
