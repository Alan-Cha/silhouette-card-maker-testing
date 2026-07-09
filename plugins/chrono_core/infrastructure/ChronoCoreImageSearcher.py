from __future__ import annotations

from typing import Optional
from re import compile

from plugins.abstraction_base.domain.Card import C
from plugins.abstraction_base.domain.CardImage import CardImage
from plugins.abstraction_base.infrastructure.ImageCachePort import DEFAULT_IMAGE_CACHE_PATH, DEFAULT_IMAGE_CONTENT_TYPE
from plugins.abstraction_base.infrastructure.ImageSearcherPort import ImageSearcherLike
from plugins.abstraction_base.infrastructure.WebRequest import perform_web_request

CHRONO_CORE_IMAGE_URL_TEMPLATE = 'https://cdn.sleeved.gg/cards/chrono-core/{SET_ID}/{CARD_ID}.webp'

class ChronoCoreImageSearcher(ImageSearcherLike[C]):

    CARD_ID_PATTERN = compile(r'^(.+)-(.+)$')

    async def find_image(self, card: C) -> Optional[CardImage]:

        match = self.CARD_ID_PATTERN.match(card.id)
        if match:
            set_id = match.group(1)

        image_url = CHRONO_CORE_IMAGE_URL_TEMPLATE.format(SET_ID=set_id, CARD_ID=card.id)
        card_image = await perform_web_request(image_url)

        return CardImage(filename = DEFAULT_IMAGE_CACHE_PATH.format(CARD_ID=card.id),
                            content_type = DEFAULT_IMAGE_CONTENT_TYPE,
                            data = card_image.content)
