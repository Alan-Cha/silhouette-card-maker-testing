from __future__ import annotations

from typing import Optional
from re import sub, compile

from plugins.abstraction_base.domain.Card import Card
from plugins.abstraction_base.domain.CardImage import CardImage
from plugins.abstraction_base.infrastructure.ImageCachePort import DEFAULT_IMAGE_CACHE_PATH, DEFAULT_IMAGE_CONTENT_TYPE
from plugins.abstraction_base.infrastructure.ImageSearcherPort import ImageSearcherLike

from plugins.abstraction_base.infrastructure.WebRequest import perform_web_request

ALTERED_API_TEMPLATE = 'https://cards.alteredcore.org/api/cards?reference={CARD_ID}'
ALTERED_IMAGE_TEMPLATE = 'https://cdn.alteredcore.org/cards/en/{SET}/{CARD_ID}.webp'

class AlteredImageSearcher(ImageSearcherLike[Card]):

    async def find_image(self, card: Card) -> Optional[CardImage]:

        api_response = await perform_web_request(ALTERED_API_TEMPLATE.format(CARD_ID=card.id))

        if api_response != None:

            card_of_response = api_response.json().get('member', [{}])[0]

            card_set = card_of_response.get('set', {}).get('reference')
            card_id = card_of_response.get('reference')
            image_url = ALTERED_IMAGE_TEMPLATE.format(SET=card_set,CARD_ID=card_id)

            card_image = await perform_web_request(image_url)
            
            if card_image != None:
                return CardImage(filename = DEFAULT_IMAGE_CACHE_PATH.format(CARD_ID=card.id),
                                content_type = DEFAULT_IMAGE_CONTENT_TYPE,
                                data = card_image.content)
