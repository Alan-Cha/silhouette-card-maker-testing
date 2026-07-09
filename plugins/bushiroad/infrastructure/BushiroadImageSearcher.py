from __future__ import annotations

from typing import Optional

from plugins.bushiroad.domain.BushiroadCard import BushiroadCard
from plugins.abstraction_base.domain.CardImage import CardImage
from plugins.abstraction_base.infrastructure.ImageCachePort import DEFAULT_IMAGE_CACHE_PATH, DEFAULT_IMAGE_CONTENT_TYPE
from plugins.abstraction_base.infrastructure.ImageSearcherPort import ImageSearcherLike
from plugins.bushiroad.domain.BushiroadGame import BushiroadGameTitle

from plugins.abstraction_base.infrastructure.WebRequest import perform_web_request

BUSHIROAD_GAME_IMAGE_URL_MAPPING = {
    BushiroadGameTitle.CARDFIGHT_VANGUARD: 'https://en.cf-vanguard.com/wordpress/wp-content/images/cardlist/{CARD_IMAGE}',
    BushiroadGameTitle.WEISS_SCHWARZ: 'https://en.ws-tcg.com/wordpress/wp-content/images/cardimages/{CARD_IMAGE}',
    BushiroadGameTitle.SHADOWVERSE_EVOLVE: 'https://en.shadowverse-evolve.com/wordpress/wp-content/images/cardlist/{CARD_IMAGE}',
    BushiroadGameTitle.GODZILLA: 'https://en.godzilla-cardgame.com/wordpress/wp-content/images/cardlist/{CARD_IMAGE}',
    BushiroadGameTitle.HOLOLIVE: 'https://en.hololive-official-cardgame.com/wp-content/images/cardlist/{CARD_IMAGE}'
}

class BushiroadImageSearcher(ImageSearcherLike[BushiroadCard]):

    async def find_image(self, card: BushiroadCard) -> Optional[CardImage]:

        image_url_template = BUSHIROAD_GAME_IMAGE_URL_MAPPING.get(card.bushiroad_game)

        if image_url_template is None:
            return
        
        image_url = image_url_template.format(CARD_IMAGE=card.front_image_url)

        card_image = await perform_web_request(image_url)

        if card_image != None:
            return CardImage(filename = DEFAULT_IMAGE_CACHE_PATH.format(CARD_ID=card.id),
                            content_type = DEFAULT_IMAGE_CONTENT_TYPE,
                            data = card_image.content)