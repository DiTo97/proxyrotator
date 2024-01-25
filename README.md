# saferequests

[![docs status](https://readthedocs.org/projects/saferequests/badge/?version=latest)](https://saferequests.readthedocs.io/en/latest/?badge=latest)
[![testing status](https://github.com/DiTo97/saferequests/actions/workflows/testing.yaml/badge.svg?branch=contrib&event=pull_request)](https://github.com/DiTo97/saferequests/actions/workflows/testing.yaml)
[![codecov status](https://codecov.io/gh/DiTo97/saferequests/graph/badge.svg?token=WH1JIVPY7N)](https://codecov.io/gh/DiTo97/saferequests)

A drop-in replacement for requests with automatic proxy rotation for web scraping and anonymity.

## usage

```python
from saferequests import ProxyRotator

# Create a ProxyRotator instance with default settings
proxy_rotator = ProxyRotator()

# Rotate to get a new proxy
proxy_rotator.rotate()

# Access the selected proxy
selected_proxy = proxy_rotator.selected
print(f"Selected Proxy: {selected_proxy}")

# Access the available proxies
available_proxies = proxy_rotator.proxy_df
print("Available Proxies:")
print(available_proxies)

# Rotate again to get another proxy
proxy_rotator.rotate()
print(f"Selected Proxy: {proxy_rotator.selected}")
```

### parallelized scraping

The module now features parallelized scraping for improved performance. The scraping of proxies from different URLs is done concurrently using asyncio and aiohttp.

### customization

```python
from saferequests import ProxyRotator

# Create a ProxyRotator with specific settings
proxy_rotator = ProxyRotator(
    anonymity='elite',
    secure=True,
    country_codes_alpha2={'US', 'CA'},
    max_num_proxies=10,
    t_refresh=300,  # Refresh every 300 seconds
    cache='proxy_cache.json',
    livecheck=True
)

# Rotate to get a new proxy
proxy_rotator.rotate()
print(f"Selected Proxy: {proxy_rotator.selected}")
```


### caching

```python
from saferequests import ProxyRotator

# Create a ProxyRotator with caching enabled
proxy_rotator = ProxyRotator(cache='proxy_cache.json')

# Rotate to get a new proxy
proxy_rotator.rotate()
print(f"Selected Proxy: {proxy_rotator.selected}")

# The available proxies are loaded from the cache
print("Available Proxies:")
print(proxy_rotator.proxy_df)
```


### live checking

```python
from saferequests import ProxyRotator

# Create a ProxyRotator with live checking enabled
proxy_rotator = ProxyRotator(livecheck=True)

# Rotate to get a new proxy, and invalid proxies will be removed immediately
proxy_rotator.rotate()
print(f"Selected Proxy: {proxy_rotator.selected}")
```
