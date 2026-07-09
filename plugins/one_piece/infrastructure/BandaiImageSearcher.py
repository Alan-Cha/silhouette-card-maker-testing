from __future__ import annotations

from typing import Optional

from plugins.abstraction_base.domain.Card import Card
from plugins.abstraction_base.domain.CardImage import CardImage
from plugins.abstraction_base.infrastructure.ImageCachePort import DEFAULT_IMAGE_CACHE_PATH, DEFAULT_IMAGE_CONTENT_TYPE
from plugins.abstraction_base.infrastructure.ImageSearcherPort import ImageSearcherLike

from plugins.abstraction_base.infrastructure.WebRequest import perform_web_request

BANDAI_URL_TEMPLATE = 'https://en.onepiece-cardgame.com/images/cardlist/card/{CARD_NUMBER}.png'

class BandaiImageSearcher(ImageSearcherLike[Card]):

    async def find_image(self, card: Card) -> Optional[CardImage]:

        card_image = await perform_web_request(BANDAI_URL_TEMPLATE.format(CARD_NUMBER=card.id))
    
        if card_image != None:
            return CardImage(filename = DEFAULT_IMAGE_CACHE_PATH.format(CARD_ID=card.id),
                            content_type = DEFAULT_IMAGE_CONTENT_TYPE,
                            data = card_image.content)