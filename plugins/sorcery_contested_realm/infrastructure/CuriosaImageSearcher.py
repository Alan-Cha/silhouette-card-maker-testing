from __future__ import annotations

from typing import Optional

from plugins.sorcery_contested_realm.domain.SorceryCard import SorceryCard
from plugins.abstraction_base.domain.CardImage import CardImage
from plugins.abstraction_base.infrastructure.ImageCachePort import DEFAULT_IMAGE_CACHE_PATH, DEFAULT_IMAGE_CONTENT_TYPE
from plugins.abstraction_base.infrastructure.ImageSearcherPort import ImageSearcherLike

from plugins.abstraction_base.infrastructure.WebRequest import perform_web_request

class CuriosaImageSearcher(ImageSearcherLike[SorceryCard]):

    async def find_image(self, card: SorceryCard) -> Optional[CardImage]:

        if card.variant_image_url is not None:
            card_image = await perform_web_request(card.variant_image_url)
        
            if card_image != None:
                return CardImage(filename = DEFAULT_IMAGE_CACHE_PATH.format(CARD_ID=card.id),
                                content_type = DEFAULT_IMAGE_CONTENT_TYPE,
                                data = card_image.content)
