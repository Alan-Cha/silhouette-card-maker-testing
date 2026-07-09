from __future__ import annotations

from httpx import AsyncClient, HTTPStatusError, RequestError, Response
from asyncio import sleep
from enum import Enum
from typing import Mapping, Any, Optional, Dict

class WebRequestType(Enum):
    GET = 'GET'
    POST = 'POST'

class PayloadType(Enum):
    JSON = 'json'
    PARAMS = 'params'
    NONE = 'none'

DEFAULT_WEB_HEADERS: Mapping[str, str] = {'user-agent': 'silhouette-card-maker/0.1', 'accept': '*/*'}
DEFAULT_PAYLOAD: Mapping[str, Any] = {}

async def perform_web_request(request_url: str,
                              fallback_url: Optional[str] = None,
                              request_type: WebRequestType = WebRequestType.GET, 
                              request_headers: Mapping[str, str] = DEFAULT_WEB_HEADERS,
                              request_payload_type: PayloadType = PayloadType.NONE, request_payload: Mapping[str, Any] = DEFAULT_PAYLOAD
                              ) -> Optional[Response]:

    kwargs: Dict[str, Any] = {
        'headers': request_headers
    }

    if request_payload_type != PayloadType.NONE:
        kwargs[request_payload_type.value] = request_payload

    try:
        async with AsyncClient(timeout=10.0, follow_redirects=True) as client:
            r = await client.request(request_type.value, request_url, **kwargs)
            r.raise_for_status()
    except HTTPStatusError as error:
        if fallback_url is None:
            print(f'{error} HTTP Error at {request_url}')
            return None
        else:
            return await perform_web_request(fallback_url)
    except RequestError as error:
        if fallback_url is None:
            print(f'Issue sending web request: {error}')
            return None
        else:
            return await perform_web_request(fallback_url)

    await sleep(0.075)

    return r
