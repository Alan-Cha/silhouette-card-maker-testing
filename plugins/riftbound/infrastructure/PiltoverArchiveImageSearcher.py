from __future__ import annotations

from typing import Optional
from re import sub, compile

from plugins.riftbound.domain.RiftboundCard import RiftboundCard
from plugins.abstraction_base.domain.CardImage import CardImage
from plugins.abstraction_base.infrastructure.ImageCachePort import DEFAULT_IMAGE_CACHE_PATH, DEFAULT_IMAGE_CONTENT_TYPE
from plugins.abstraction_base.infrastructure.ImageSearcherPort import ImageSearcherLike

from plugins.abstraction_base.infrastructure.WebRequest import perform_web_request

PILTOVER_URL_TEMPLATE = 'https://cdn.piltoverarchive.com/cards/{CARD_NUMBER}.webp'

class PiltoverArchiveImageSearcher(ImageSearcherLike[RiftboundCard]):

    ALTERNATE_ART_PATTERN = compile(r'^([A-Z0-9]+-\d+)a$')

    async def find_image(self, card: RiftboundCard) -> Optional[CardImage]:

        match = self.ALTERNATE_ART_PATTERN.search(card.card_number)
        fallback_url = None if not match else PILTOVER_URL_TEMPLATE.format(CARD_NUMBER=match.group(1))
        card_image = await perform_web_request(PILTOVER_URL_TEMPLATE.format(CARD_NUMBER=card.card_number), fallback_url)
    
        if card_image != None:
            return CardImage(filename = DEFAULT_IMAGE_CACHE_PATH.format(CARD_ID=card.id),
                            content_type = DEFAULT_IMAGE_CONTENT_TYPE,
                            data = card_image.content)
