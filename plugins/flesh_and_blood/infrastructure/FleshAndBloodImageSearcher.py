from __future__ import annotations

from typing import Optional, Mapping, Any
from re import sub
from unicodedata import normalize

from plugins.flesh_and_blood.domain.FleshAndBloodCard import FleshAndBloodCard
from plugins.flesh_and_blood.domain.Pitch import Pitch
from plugins.abstraction_base.domain.CardImage import CardImage
from plugins.abstraction_base.infrastructure.ImageCachePort import DEFAULT_IMAGE_CACHE_PATH, DEFAULT_IMAGE_CONTENT_TYPE
from plugins.abstraction_base.infrastructure.ImageSearcherPort import ImageSearcherLike

from plugins.abstraction_base.infrastructure.WebRequest import perform_web_request

FLESH_AND_BLOOD_API_URL_TEMPLATE = 'https://api.cardvault.fabtcg.com/carddb/api/v1/advanced-search/?name={CARD_NAME}{PITCH}'

class FleshAndBloodImageSearcher(ImageSearcherLike[FleshAndBloodCard]):
    async def find_image(self, card: FleshAndBloodCard) -> Optional[CardImage]:

        print(card.name)
        sanitized = sub(r'[^A-Za-z0-9 ]+', '', card.name)
        slugified = sub(r'\s+', '+', sanitized).lower()
        pitch_argument = f'&pitch_lookup=exact&pitch={card.pitch.value}' if card.pitch != Pitch.NONE else ''
        
        request_response = await perform_web_request(FLESH_AND_BLOOD_API_URL_TEMPLATE.format(CARD_NAME=slugified, PITCH=pitch_argument))
        
        if request_response != None:
            json_response = request_response.json()
            card_from_response: Mapping[str, Any] = json_response.get('results')[0] if len(json_response.get('results')) > 0 else {}

            image_url = card_from_response.get('faces', [{}])[0].get('image', {}).get('normal', None)

            if image_url != None:
                card_image = await perform_web_request(image_url)

                return CardImage(filename = DEFAULT_IMAGE_CACHE_PATH.format(CARD_ID=card.id),
                                content_type = DEFAULT_IMAGE_CONTENT_TYPE,
                                data = card_image.content)
