from __future__ import annotations

from re import compile

from plugins.bushiroad.domain.BushiroadCard import BushiroadCard
from plugins.bushiroad.domain.BushiroadGame import BUSHIROAD_GAME_TITLE_ID_MAPPING
from plugins.abstraction_base.domain.Deck import Deck
from plugins.abstraction_base.infrastructure.DeckSearcherPort import DeckSearcherLike
from plugins.abstraction_base.infrastructure.WebRequest import perform_web_request, DEFAULT_WEB_HEADERS
from plugins.abstraction_base.infrastructure.StringManipulation import normalize_string
from plugins.bushiroad.domain.BushiroadGame import BUSHIROAD_GAME_TITLE_ID_MAPPING

class BushiroadDeckSearcher(DeckSearcherLike[BushiroadCard]):

    URL_PATTERN = compile(r'https?:\/\/decklog(?:-en)?\.bushiroad\.com\/view\/(\w+)\s*')
    API_TEMPLATE = 'https://decklog-en.bushiroad.com/system/app/api/view/{DECK_CODE}'
    DECKLOG_REFERER = 'https://decklog-en.bushiroad.com/'

    async def is_url_for_deck(self, deck_url: str):
        return bool(self.URL_PATTERN.match(deck_url))
    
    async def extract_deck_from_url(self, deck_url: str):
        extracted_deck: list[BushiroadCard] = []

        match = self.URL_PATTERN.match(deck_url)
        if match:
            deck_code = match.group(1).strip()
            api_url_for_deck = self.API_TEMPLATE.format(DECK_CODE=deck_code)
            headers = DEFAULT_WEB_HEADERS
            headers['referer'] = self.DECKLOG_REFERER
            api_response = await perform_web_request(api_url_for_deck, request_headers=headers)

            if api_response is None:
                return extracted_deck

            json_of_response = api_response.json()
            bushiroad_game = BUSHIROAD_GAME_TITLE_ID_MAPPING.get(str(json_of_response.get('game_title_id')))

            if bushiroad_game is None:
                return

            main_deck = json_of_response.get('list') or []
            leader = json_of_response.get('p_list') or []
            evolve_deck = json_of_response.get('sub_list') or []
            unmapped_deck = main_deck + leader + evolve_deck

            card_index = 0
            for card in unmapped_deck:
                card_index += 1

                card_name = card.get('name')
                card_id = normalize_string(card_name)
                card_quantity = int(card.get('num'))
                front_url = card.get('img', '').strip()
                back_url = ''
                if card.get('custom_param') is not None and card.get('custom_param').get('is_bothsides'):
                    back_url = card.get('custom_param').get('rev_img', '').strip()

                extracted_card: BushiroadCard = BushiroadCard(
                    id = card_id,
                    name = card_name,
                    quantity = card_quantity,
                    placements = [card_index for _ in range(card_quantity)],
                    front_image = None,
                    back_image = None,
                    bushiroad_game = bushiroad_game,
                    front_image_url = front_url,
                    back_image_url = back_url
                )

                extracted_deck.append(extracted_card)

        return Deck(cards=extracted_deck)