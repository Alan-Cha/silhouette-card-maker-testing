from __future__ import annotations

from typing import Optional, Mapping, Any
from urllib.parse import quote_plus

from plugins.abstraction_base.domain.Card import Card
from plugins.abstraction_base.domain.CardImage import CardImage
from plugins.abstraction_base.infrastructure.ImageCachePort import DEFAULT_IMAGE_CACHE_PATH, DEFAULT_IMAGE_CONTENT_TYPE
from plugins.abstraction_base.infrastructure.ImageSearcherPort import ImageSearcherLike

from plugins.abstraction_base.infrastructure.WebRequest import perform_web_request

WARLORD_CCG_DB_API_URL_TEMPLATE = 'https://warlordccgdb.com/api/cards?search={CARD_NAME}&page=1&pageSize=25&sortBy=name&sortDir=asc'
WARLORD_CCG_DB_IMAGE_URL_TEMPLATE = 'https://warlordccgdb.com/api/images/{IMAGE_PATH}'

class WarlordCCGDBImageSearcher(ImageSearcherLike[Card]):
    async def find_image(self, card: Card) -> Optional[CardImage]:

        print(card.id)

        query_url = WARLORD_CCG_DB_API_URL_TEMPLATE.format(CARD_NAME=quote_plus(card.id))
        request_response = await perform_web_request(query_url)

        if request_response != None:
            json_response = request_response.json()
            cards_from_response: Mapping[str, Any] = json_response.get('items', [])

            image_url = None if not cards_from_response else WARLORD_CCG_DB_IMAGE_URL_TEMPLATE.format(IMAGE_PATH=cards_from_response[0].get('imagePath'))

            if image_url != None:
                card_image = await perform_web_request(image_url)

                return CardImage(filename = DEFAULT_IMAGE_CACHE_PATH.format(CARD_ID=card.id),
                                content_type = DEFAULT_IMAGE_CONTENT_TYPE,
                                data = card_image.content)