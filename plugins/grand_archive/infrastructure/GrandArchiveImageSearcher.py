from __future__ import annotations

from typing import Optional
from re import sub

from plugins.abstraction_base.domain.Card import C
from plugins.abstraction_base.domain.CardImage import CardImage
from plugins.abstraction_base.infrastructure.ImageCachePort import DEFAULT_IMAGE_CACHE_PATH, DEFAULT_IMAGE_CONTENT_TYPE
from plugins.abstraction_base.infrastructure.ImageSearcherPort import ImageSearcherLike

from plugins.abstraction_base.infrastructure.WebRequest import perform_web_request

GRAND_ARCHIVE_CARD_URL_TEMPLATE = 'https://api.gatcg.com/cards/{NAME}'
GRAND_ARCHIVE_CARD_ART_URL_TEMPLATE = 'https://api.gatcg.com/{CARD_ART_SUFFIX}'

class GrandArchiveImageSearcher(ImageSearcherLike[C]):
    async def find_image(self, card: C) -> Optional[CardImage]:

        print(card.name)
        sanitized = sub(r'[^A-Za-z0-9 \-]+', '', card.name)
        slugified = sub(r'\s+', '-', sanitized).lower()
        name_response = await perform_web_request(GRAND_ARCHIVE_CARD_URL_TEMPLATE.format(NAME=slugified))

        card_art_suffix = name_response.json().get('editions', [{}])[0].get('image', None)
    
        if card_art_suffix != None:
            card_image = await perform_web_request(GRAND_ARCHIVE_CARD_ART_URL_TEMPLATE.format(CARD_ART_SUFFIX=card_art_suffix))

            return CardImage(filename = DEFAULT_IMAGE_CACHE_PATH.format(CARD_ID=card.id),
                            content_type = DEFAULT_IMAGE_CONTENT_TYPE,
                            data = card_image.content)
