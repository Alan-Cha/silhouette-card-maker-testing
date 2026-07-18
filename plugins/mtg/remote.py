import pathlib
from datetime import timedelta
import time
from typing import Any, Callable

import joblib
import requests

# CONFIGURABLE
# cmdr deck is ~100mb, so store the last two
_CACHE_SIZE_MAX = 256 * 1024 * 1024
# assume the data does not change that often and we can keep the last day
_CACHE_AGE_MAX = timedelta(days=1)
_GET_RETRIES = 3
_GET_RETRY_DELAY = timedelta(seconds=30)

# CONSTANTS
_HTTP_RATE_LIMITED = 429
_CACHE_DIR = pathlib.Path(__file__).parent / ".cache-remote"
_CACHE_DIR.mkdir(exist_ok=True)
_SCRYFALL_RETRY_DELAY_MIN = timedelta(seconds=30)


_GET_HEADERS = {
    'user-agent': 'silhouette-card-maker/0.1',
    'accept': '*/*',
}

# STATE
_cache = joblib.Memory(
    # Don't bother with compression. Majority of it is images and those are incompressible.
    location=_CACHE_DIR,
    verbose=0,
)
_session = requests.Session()

# INVARIANTS
assert 0 < _CACHE_SIZE_MAX
assert timedelta() < _CACHE_AGE_MAX
assert 0 < _GET_RETRIES
assert _SCRYFALL_RETRY_DELAY_MIN <= _GET_RETRY_DELAY, "Scryfall requires at least 30s between retries"

def memo(func: Callable | None = None):
    if func is None: # no partial args at this time, just give a plain wrapper
      return lambda func: memo(func)

    return _cache.cache(func)

def get(query: str, params: dict[str, Any] | None = None) -> requests.Response:
    for i in range(_GET_RETRIES):
        r = _session.get(query, params=params, headers = _GET_HEADERS)
        # Rate limit check - Scryfall requires 30 second wait per their documentation
        if r.status_code != _HTTP_RATE_LIMITED:
            r.raise_for_status()
            return r

        print(f"Hit rate limit ({_HTTP_RATE_LIMITED}), waiting {_GET_RETRY_DELAY} seconds before retry {i + 1}/{_GET_RETRIES}...")
        time.sleep(_GET_RETRY_DELAY.total_seconds())

    assert isinstance(r, requests.Response)
    print(f"Warning: Hit rate limit {_GET_RETRIES} times for {query}, giving up.")
    raise requests.exceptions.HTTPError(f"Max retries ({_GET_RETRIES}) exceeded query: {query}", response=r)

def cache_trim():
    _cache.reduce_size(
        bytes_limit=_CACHE_SIZE_MAX,
        age_limit=_CACHE_AGE_MAX,
    )
