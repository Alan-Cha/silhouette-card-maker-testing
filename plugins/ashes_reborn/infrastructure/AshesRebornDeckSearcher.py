from __future__ import annotations

from re import compile

from plugins.abstraction_base.domain.Card import Card
from plugins.abstraction_base.domain.Deck import Deck
from plugins.abstraction_base.infrastructure.DeckSearcherPort import DeckSearcherLike
from plugins.abstraction_base.infrastructure.WebRequest import perform_web_request

class AshesRebornDeckSearcher(DeckSearcherLike[Card]):

    ASHES_URL_PATTERN = compile(r'https:\/\/ashes.live\/decks\/share\/(.+)')
    ASHES_DB_URL_PATTERN = compile(r'https:\/\/ashesdb.plaidhatgames.com\/decks\/share\/(.+)')

    ASHES_API_TEMPLATE = 'https://api.ashes.live/v2/decks/shared/{DECK_ID}'
    ASHES_DB_API_TEMPLATE = 'https://apiasheslive.plaidhatgames.com/v2/decks/shared/{DECK_ID}'

    async def is_url_for_deck(self, deck_url: str):
        return bool(self.ASHES_URL_PATTERN.match(deck_url) or self.ASHES_DB_URL_PATTERN.match(deck_url))
    
    async def extract_deck_from_url(self, deck_url: str):
        extracted_deck: list[Card] = []

        ashes_match = self.ASHES_URL_PATTERN.match(deck_url)
        ashes_db_match = self.ASHES_DB_URL_PATTERN.match(deck_url)
        if ashes_match or ashes_db_match:
            deck_id = ashes_match.group(1).strip() if ashes_match else ashes_db_match.group(1).strip()
            api_url_for_deck = self.ASHES_API_TEMPLATE.format(DECK_ID=deck_id) if ashes_match else self.ASHES_DB_API_TEMPLATE.format(DECK_ID=deck_id)
            api_response = await perform_web_request(api_url_for_deck)

            if api_response is None:
                return extracted_deck

            json_of_response = api_response.json()

            phoenixborn = [json_of_response.get('phoenixborn')] or []
            main = json_of_response.get('cards', [])
            conjuration = json_of_response.get('conjurations', [])
            deck = phoenixborn + main + conjuration

            card_index = 0
            for card in deck:
                card_index += 1

                card_id = card.get('stub')
                card_name = card.get('name')
                card_quantity = card.get('count') or 1

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