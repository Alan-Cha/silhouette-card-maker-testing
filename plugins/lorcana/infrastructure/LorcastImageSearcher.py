from __future__ import annotations

from typing import Optional, Mapping, Any
from re import sub
from unicodedata import normalize

from plugins.lorcana.domain.LorcanaCard import LorcanaCard
from plugins.abstraction_base.domain.CardImage import CardImage
from plugins.abstraction_base.infrastructure.ImageCachePort import DEFAULT_IMAGE_CACHE_PATH, DEFAULT_IMAGE_CONTENT_TYPE
from plugins.abstraction_base.infrastructure.ImageSearcherPort import ImageSearcherLike

from plugins.abstraction_base.infrastructure.WebRequest import perform_web_request

LORCAST_API_URL_TEMPLATE = 'https://api.lorcast.com/v0/cards/search?q={CARD_NAME}{ENCHANTED}'

class LorcastImageSearcher(ImageSearcherLike[LorcanaCard]):

    async def find_image(self, card: LorcanaCard) -> Optional[CardImage]:

        print(card.name)
        slugified = sub(r'[^\w]', '+', card.name)
        enchanted_argument = '+rarity:enchanted' if card.enchanted else ''

        api_url = LORCAST_API_URL_TEMPLATE.format(CARD_NAME=slugified, ENCHANTED=enchanted_argument)
        request_response = await perform_web_request(api_url)
        
        if request_response != None:
            json_response = request_response.json()
            card_from_response: Mapping[str, Any] = json_response.get('results')[0] if len(json_response.get('results')) > 0 else {}

            image_uris = card_from_response.get('image_uris', {}).get('digital', {})

            image_url = None
            if 'large' in image_uris:
                image_url = image_uris.get('large')
            elif 'medium' in image_uris:
                image_url = image_uris.get('medium')
            elif 'small' in image_uris:
                image_url = image_uris.get('small')

            if image_url != None:
                card_image = await perform_web_request(image_url)

                return CardImage(filename = DEFAULT_IMAGE_CACHE_PATH.format(CARD_ID=card.id),
                                content_type = DEFAULT_IMAGE_CONTENT_TYPE,
                                data = card_image.content)
