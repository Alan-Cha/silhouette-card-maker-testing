from __future__ import annotations

from typing import Optional, Mapping, Any
from re import sub
from unicodedata import normalize

from plugins.abstraction_base.domain.Card import C
from plugins.abstraction_base.domain.CardImage import CardImage
from plugins.abstraction_base.infrastructure.ImageCachePort import DEFAULT_IMAGE_CACHE_PATH, DEFAULT_IMAGE_CONTENT_TYPE
from plugins.abstraction_base.infrastructure.ImageSearcherPort import ImageSearcherLike

from plugins.abstraction_base.infrastructure.WebRequest import perform_web_request

CYBERPUNK_API_URL_TEMPLATE = 'https://api.netdeck.gg/api/cards/cyberpunk?q=n:\"{CARD_NAME}\"&limit=60&offset=0'

class CyberpunkImageSearcher(ImageSearcherLike[C]):
    async def find_image(self, card: C) -> Optional[CardImage]:

        print(card.name)
		# Replace whitespace with + (ex. 'V - Streetkid', 'Royce - Psycho on the Edge', 'T-Bug - Amateur Philosopher')
        slugified = sub(r'\s+', '+', card.name)
        
        request_response = await perform_web_request(CYBERPUNK_API_URL_TEMPLATE.format(CARD_NAME=slugified))
        
        if request_response != None:
            json_response = request_response.json()
            card_from_response: Mapping[str, Any] = json_response.get('items')[0] if len(json_response.get('items')) > 0 else {}

            print_number = card_from_response.get('print_number')
            image_url = card_from_response.get('image_url')

            card.id = card.id if card.id != None else f'{normalize('NFD', print_number).upper()}'

            if image_url != None:
                card_image = await perform_web_request(image_url)

                return CardImage(filename = DEFAULT_IMAGE_CACHE_PATH.format(CARD_ID=card.id),
                                content_type = DEFAULT_IMAGE_CONTENT_TYPE,
                                data = card_image.content)
