import requests

from .rotator import ProxyRotator


class ProxiedSession(requests.Session):
    def __init__(self, proxy_rotator=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.proxy_rotator = proxy_rotator or ProxyRotator()
        self.current_proxy = None

    def request(self, method, url, *args, **kwargs):
        if not self.current_proxy or not self.proxy_successful(
            method, url, *args, **kwargs
        ):
            self.proxy_rotator.rotate()
            self.current_proxy = self.proxy_rotator.selected

        if self.current_proxy:
            kwargs.setdefault(
                "proxies", {"http": self.current_proxy, "https": self.current_proxy}
            )

        try:
            response = super().request(method, url, *args, **kwargs)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            if isinstance(e, requests.HTTPError) and e.response.status_code == 404:
                raise e
            else:
                print(
                    f"Request failed with non-404 error. Retrying with the same proxy..."
                )
                return self.request(method, url, *args, **kwargs)

    def proxy_successful(self, method, url, *args, **kwargs):
        try:
            response = super().request(method, url, *args, **kwargs)
            response.raise_for_status()
            return True
        except requests.RequestException as e:
            return False

    def close(self):
        pass
