from __future__ import annotations

from typing import Optional
from re import sub, compile

from plugins.riftbound.domain.RiftboundCard import RiftboundCard
from plugins.abstraction_base.domain.CardImage import CardImage
from plugins.abstraction_base.infrastructure.ImageCachePort import DEFAULT_IMAGE_CACHE_PATH, DEFAULT_IMAGE_CONTENT_TYPE
from plugins.abstraction_base.infrastructure.ImageSearcherPort import ImageSearcherLike

from plugins.abstraction_base.infrastructure.WebRequest import perform_web_request

RIFTMANA_URL_TEMPLATE = 'https://riftmana.com/wp-content/uploads/Cards/{CARD_NUMBER}.webp'

class RiftManaImageSearcher(ImageSearcherLike[RiftboundCard]):

    ALTERNATE_ART_PATTERN = compile(r'^([A-Z0-9]+-\d+)a$')

    async def find_image(self, card: RiftboundCard) -> Optional[CardImage]:

        if card.id is not None:
            match = self.ALTERNATE_ART_PATTERN.search(card.id)
            fallback_url = None if not match else RIFTMANA_URL_TEMPLATE.format(CARD_NUMBER=match.group(1))
            card_image = await perform_web_request(RIFTMANA_URL_TEMPLATE.format(CARD_NUMBER=card.id), fallback_url)
        
            if card_image != None:
                return CardImage(filename = DEFAULT_IMAGE_CACHE_PATH.format(CARD_ID=card.id),
                                content_type = DEFAULT_IMAGE_CONTENT_TYPE,
                                data = card_image.content)
