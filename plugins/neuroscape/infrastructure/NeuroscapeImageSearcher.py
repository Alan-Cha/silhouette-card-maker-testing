from __future__ import annotations

from typing import Optional, Mapping, Any

from plugins.abstraction_base.domain.Card import C
from plugins.abstraction_base.domain.CardImage import CardImage
from plugins.abstraction_base.infrastructure.ImageCachePort import DEFAULT_IMAGE_CACHE_PATH, DEFAULT_IMAGE_CONTENT_TYPE
from plugins.abstraction_base.infrastructure.ImageSearcherPort import ImageSearcherLike
from plugins.abstraction_base.infrastructure.WebRequest import perform_web_request, WebRequestType, PayloadType, DEFAULT_WEB_HEADERS

NEUROSCAPE_API_URL = 'https://api.admin.carde.io/api/v2/deckbuilder/cards/search-with-filters/'
NEUROSCAPE_REFERER = 'https://playneuroscape.com/'
NEUROSCAPE_PAYLOAD_TEMPLATE = {
    'game_id': 134,
    'query': 'CARD NAME',
    'filters': {},
    'sort_by': 'name',
    'sort_order': 'asc',
    'limit': 50,
    'offset': 0
}

class NeuroscapeImageSearcher(ImageSearcherLike[C]):
    async def find_image(self, card: C) -> Optional[CardImage]:

        request_headers = DEFAULT_WEB_HEADERS
        request_headers['referer'] = NEUROSCAPE_REFERER

        request_payload = NEUROSCAPE_PAYLOAD_TEMPLATE
        request_payload['query'] = card.name

        print(card.name)

        request_response = await perform_web_request(NEUROSCAPE_API_URL,
                                                     request_type=WebRequestType.POST,
                                                     request_payload_type=PayloadType.JSON, request_payload=request_payload)
        
        if request_response != None:
            json_response = request_response.json()
            card_from_response: Mapping[str, Any] = json_response.get('cards')[0]

            image_url = card_from_response.get('image_url')

            card_image = await perform_web_request(image_url)

            return CardImage(filename = DEFAULT_IMAGE_CACHE_PATH.format(CARD_ID=card.id),
                             content_type = DEFAULT_IMAGE_CONTENT_TYPE,
                             data = card_image.content)
