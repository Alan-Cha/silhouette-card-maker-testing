from __future__ import annotations

from re import compile

from plugins.abstraction_base.domain.Card import Card
from plugins.abstraction_base.domain.Deck import Deck
from plugins.abstraction_base.infrastructure.DeckSearcherPort import DeckSearcherLike
from plugins.abstraction_base.infrastructure.WebRequest import perform_web_request

class ChronoCoreDeckSearcher(DeckSearcherLike[Card]):

    URL_PATTERN = compile(r'https:\/\/sleeved.gg\/chrono-core\/decks\/(.+)')
    API_TEMPLATE = 'https://api.sleeved.gg/decks/{DECK_ID}'

    async def is_url_for_deck(self, deck_url: str):
        return bool(self.URL_PATTERN.match(deck_url))
    
    async def extract_deck_from_url(self, deck_url: str):
        extraced_cards_of_deck: list[Card]= []

        match = self.URL_PATTERN.match(deck_url)
        if match:
            deck_id = match.group(1).strip()
            api_url_for_deck = self.API_TEMPLATE.format(DECK_ID=deck_id)
            api_response = await perform_web_request(api_url_for_deck)

            if api_response is None:
                return extraced_cards_of_deck

            json_of_response = api_response.json()

            card_list = json_of_response.get('cards', [])

            card_index = 0
            for card in card_list:
                card_index += 1

                card_id = card.get('id')
                card_name = card.get('displayLabel')
                card_quantity = card.get('quantity')

                extracted_card: Card = Card(
                    id = card_id,
                    name = card_name,
                    quantity = card_quantity,
                    placements = [card_index for _ in range(card_quantity)],
                    front_image = None,
                    back_image = None
                )

                extraced_cards_of_deck.append(extracted_card)

        return Deck(cards=extraced_cards_of_deck)