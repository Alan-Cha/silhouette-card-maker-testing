from __future__ import annotations

from typing import Optional

from plugins.abstraction_base.domain.Card import C
from plugins.abstraction_base.domain.CardImage import CardImage
from plugins.abstraction_base.infrastructure.ImageCachePort import DEFAULT_IMAGE_CACHE_PATH, DEFAULT_IMAGE_CONTENT_TYPE
from plugins.abstraction_base.infrastructure.ImageSearcherPort import ImageSearcherLike
from plugins.abstraction_base.infrastructure.WebRequest import perform_web_request

COOKIE_RUN_IMAGE_URL_TEMPLATE = 'https://storage.googleapis.com/cardeio-images/cookie-run-braverse/cards/small/{CARD_ID}.png'
OLD_COOKIE_RUN_IMAGE_URL_TEMPLATE = 'https://storage.googleapis.com/cardeio-images/cookie-run-braverse/cards/small/{CARD_ID}.webp'

class CookieRunImageSearcher(ImageSearcherLike[C]):
    async def find_image(self, card: C) -> Optional[CardImage]:

        print(card.name, card.id)

        image_url = COOKIE_RUN_IMAGE_URL_TEMPLATE.format(CARD_ID=card.id)
        old_image_url = OLD_COOKIE_RUN_IMAGE_URL_TEMPLATE.format(CARD_ID=card.id)
        card_image = await perform_web_request(image_url, fallback_url=old_image_url)

        return CardImage(filename = DEFAULT_IMAGE_CACHE_PATH.format(CARD_ID=card.id),
                            content_type = DEFAULT_IMAGE_CONTENT_TYPE,
                            data = card_image.content)
