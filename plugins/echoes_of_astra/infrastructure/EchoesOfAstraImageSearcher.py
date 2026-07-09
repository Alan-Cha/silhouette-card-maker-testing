from __future__ import annotations

from typing import Optional

from plugins.abstraction_base.domain.Card import Card
from plugins.abstraction_base.domain.CardImage import CardImage
from plugins.abstraction_base.infrastructure.ImageCachePort import DEFAULT_IMAGE_CACHE_PATH, DEFAULT_IMAGE_CONTENT_TYPE
from plugins.abstraction_base.infrastructure.ImageSearcherPort import ImageSearcherLike

from plugins.abstraction_base.infrastructure.WebRequest import perform_web_request

ECHOES_OF_ASTRA_URL = 'https://api.echoesofastra.com/getallcards?allowPrivate=false&accessKey=fjli32j3inrld'

class EchoesOfAstraImageSearcher(ImageSearcherLike[Card]):

    async def find_image(self, card: Card) -> Optional[CardImage]:

        # This is likely better to have as a method within the image cacher, on instantiation then fallback to this

        data = await perform_web_request(ECHOES_OF_ASTRA_URL)
        cards_from_catalog = data.json()

        for card_in_catalog in cards_from_catalog:
            if card_in_catalog.get('cardName') == card.id:
                card_image = await perform_web_request(card_in_catalog.get('cardImageLargeUrl'))
    
        if card_image != None:
            return CardImage(filename = DEFAULT_IMAGE_CACHE_PATH.format(CARD_ID=card.id),
                            content_type = DEFAULT_IMAGE_CONTENT_TYPE,
                            data = card_image.content)