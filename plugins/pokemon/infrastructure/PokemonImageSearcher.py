from __future__ import annotations

from typing import Optional

from plugins.pokemon.domain.PokemonCard import PokemonCard
from plugins.abstraction_base.domain.CardImage import CardImage
from plugins.abstraction_base.infrastructure.ImageCachePort import DEFAULT_IMAGE_CACHE_PATH, DEFAULT_IMAGE_CONTENT_TYPE
from plugins.abstraction_base.infrastructure.ImageSearcherPort import ImageSearcherLike
from plugins.abstraction_base.infrastructure.WebRequest import perform_web_request, PayloadType

LIMITLESS_TCG_URL_TEMPLATE = 'https://limitlesstcg.nyc3.cdn.digitaloceanspaces.com/tpci/{SET_ID}/{SET_ID}_{CARD_NUMBER}_R_EN_LG.png'

LIMITLESS_POCKET_URL_TEMPLATE = 'https://limitlesstcg.nyc3.cdn.digitaloceanspaces.com/pocket/{SET_ID}/{SET_ID}_{CARD_NUMBER}_EN_SM.webp'
# pokemontcg.io search API: queries by name/number and returns JSON with image
# URLs. Requires two requests (search + image download).
POKEMONTCG_API_URL = 'https://api.pokemontcg.io/v2/cards'
# pokemontcg.io images CDN: serves card images as static files. If you know
# the set ID and card number, you can download the image directly in one
# request without querying the API.
POKEMONTCG_IMAGE_URL_TEMPLATE = 'https://images.pokemontcg.io/{SET_ID}/{CARD_NUMBER}_hires.png'

# Static mapping from Limitless set codes to pokemontcg.io set IDs.
# The Limitless CDN only hosts images for HGSS-era sets (2010) and newer.
# Older sets use different set IDs on pokemontcg.io, so this mapping is needed
# to construct direct image URLs. This list is complete and will never need
# updating, since no new sets will be added to these older eras.
LIMITLESS_TO_POKEMONTCG_SET_ID = {
    # WotC era
    'BS': 'base1', 'JU': 'base2', 'FO': 'base3', 'BS2': 'base4',
    'TR': 'base5', 'G1': 'gym1', 'G2': 'gym2',
    'N1': 'neo1', 'N2': 'neo2', 'SI': 'si1', 'N3': 'neo3', 'N4': 'neo4',
    'LC': 'base6', 'E1': 'ecard1', 'E2': 'ecard2', 'E3': 'ecard3',
    'WP': 'basep', 'BG': 'bp',
    # EX era
    'RS': 'ex1', 'SS': 'ex2', 'DR': 'ex3', 'MA': 'ex4',
    'HL': 'ex5', 'RG': 'ex6', 'TRR': 'ex7', 'DX': 'ex8',
    'EM': 'ex9', 'UF': 'ex10', 'DS': 'ex11', 'LM': 'ex12',
    'HP': 'ex13', 'CG': 'ex14', 'DF': 'ex15', 'PK': 'ex16',
    'NP': 'np',
    'P1': 'pop1', 'P2': 'pop2', 'P3': 'pop3', 'P4': 'pop4', 'P5': 'pop5',
    # DP/Platinum era
    'DP': 'dp1', 'MT': 'dp2', 'SW': 'dp3', 'GE': 'dp4',
    'MD': 'dp5', 'LA': 'dp6', 'SF': 'dp7',
    'PL': 'pl1', 'RR': 'pl2', 'SV': 'pl3', 'AR': 'pl4',
    'RM': 'ru1',
    'P6': 'pop6', 'P7': 'pop7', 'P8': 'pop8', 'P9': 'pop9',
}

POKEMONTCG_QUERY_TEMPLATE = 'name:"{CARD_NAME}" number:{CARD_NUMBER}'

_failed_tcg_sets = set()
_failed_pocket_sets = set()

class PokemonImageSearcher(ImageSearcherLike[PokemonCard]):
    async def find_image(self, card: PokemonCard) -> Optional[CardImage]:

        print(card.id)

        if card.set not in _failed_tcg_sets:
            url = LIMITLESS_TCG_URL_TEMPLATE.format(SET_ID=card.set, CARD_NUMBER=str(card.card_number).zfill(3))
            card_image = await perform_web_request(url)
            if card_image is None:
                _failed_tcg_sets.add(card.set)
        
        if card_image is None and card.set not in _failed_pocket_sets:
            url = LIMITLESS_POCKET_URL_TEMPLATE.format(SET_ID=card.set, CARD_NUMBER=str(card.card_number).zfill(3))
            card_image = await perform_web_request(url)
            if card_image is None:
                _failed_pocket_sets.add(card.set)

        if card_image is None and card.set in LIMITLESS_TO_POKEMONTCG_SET_ID:
            pokemontcg_set_id = LIMITLESS_TO_POKEMONTCG_SET_ID[card.set]
            url = POKEMONTCG_IMAGE_URL_TEMPLATE.format(SET_ID=pokemontcg_set_id, CARD_NUMBER=card.card_number)
            card_image = await perform_web_request(url)

        if card_image is None:
            query = POKEMONTCG_QUERY_TEMPLATE.format(CARD_NAME=card.name, CARD_NUMBER=card.card_number)
            payload = {'q': query}
            request_response = await perform_web_request(request_url=POKEMONTCG_API_URL, request_payload_type=PayloadType.PARAMS, request_payload=payload)
            cards = request_response.json().get('data', [])

            if cards:
                image_url = cards[0].get('images', {}).get('large')
                card_image = await perform_web_request(image_url)

        if card_image != None:

            return CardImage(filename = DEFAULT_IMAGE_CACHE_PATH.format(CARD_ID=card.id),
                             content_type = DEFAULT_IMAGE_CONTENT_TYPE,
                             data = card_image.content)
