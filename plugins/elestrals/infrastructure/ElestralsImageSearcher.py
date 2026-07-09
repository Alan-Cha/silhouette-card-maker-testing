from __future__ import annotations

from typing import Optional, Mapping, Any
from re import findall

from plugins.abstraction_base.domain.Card import C
from plugins.abstraction_base.domain.CardImage import CardImage
from plugins.abstraction_base.infrastructure.ImageCachePort import DEFAULT_IMAGE_CACHE_PATH, DEFAULT_IMAGE_CONTENT_TYPE
from plugins.abstraction_base.infrastructure.ImageSearcherPort import ImageSearcherLike

from plugins.abstraction_base.infrastructure.WebRequest import perform_web_request

ELESTRALS_URL_TEMPLATE = 'https://collect.elestrals.com/cards/{CARD_ID}'
ELESTRALS_IMAGE_PATTERN = r'https://res\.cloudinary\.com/drmapg0vi/image/upload/[^"\'<> ]+'

class ElestralsImageSearcher(ImageSearcherLike[C]):
    async def find_image(self, card: C) -> Optional[CardImage]:

        print(card.id)

        request_response = await perform_web_request(ELESTRALS_URL_TEMPLATE.format(CARD_ID=card.id))
        
        if request_response != None:
            website_body = request_response.text

            match = findall(ELESTRALS_IMAGE_PATTERN, website_body)

            if match:
                for image_url in match:
                    if "NoWatermark" in image_url: break
                card_image = await perform_web_request(image_url[:-1])

                return CardImage(filename = DEFAULT_IMAGE_CACHE_PATH.format(CARD_ID=card.id),
                                content_type = DEFAULT_IMAGE_CONTENT_TYPE,
                                data = card_image.content)
