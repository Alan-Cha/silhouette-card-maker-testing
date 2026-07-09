from __future__ import annotations

from re import compile

from plugins.abstraction_base.domain.Card import Card
from plugins.abstraction_base.domain.Deck import Deck
from plugins.abstraction_base.infrastructure.DeckSearcherPort import DeckSearcherLike
from plugins.abstraction_base.infrastructure.WebRequest import perform_web_request

class CookieRunDeckSearcher(DeckSearcherLike[Card]):

    URL_PATTERN = compile(r'https:\/\/play\.cookieruntcg\.com\/decks\/(.+)')
    API_TEMPLATE = 'https://play-api.carde.io/v1/decks/{DECK_ID}'

    async def is_url_for_deck(self, deck_url: str):
        return bool(self.URL_PATTERN.match(deck_url))
    
    async def extract_deck_from_url(self, deck_url: str):
        extracted_deck: Deck[Card] = []

        match = self.URL_PATTERN.match(deck_url)
        if match:
            deck_id = match.group(1).strip()
            api_url_for_deck = self.API_TEMPLATE.format(DECK_ID=deck_id)
            api_response = await perform_web_request(api_url_for_deck)

            if api_response is None:
                return extracted_deck

            json_of_response = api_response.json()
            data_of_json = json_of_response.get('data')

            card_list = data_of_json.get('deck', {}).get('sections', [])
            unmapped_deck = card_list[0].get('cards', [])
            unmapped_deck_details = { card.get('_id'): card for card in data_of_json.get('cards', []) }

            card_index = 0
            for card in unmapped_deck:
                card_index += 1
                card_details = unmapped_deck_details[card.get('cardId')]

                card_id = card_details.get('slug')
                card_name = card_details.get('name')
                card_quantity = card.get('count')

                extracted_card: Card = Card(
                    id = card_id,
                    name = card_name,
                    quantity = card_quantity,
                    placements = [card_index for _ in range(card_quantity)],
                    front_image = None,
                    back_image = None
                )

                extracted_deck.append(extracted_card)

        return Deck(cards=extracted_deck)