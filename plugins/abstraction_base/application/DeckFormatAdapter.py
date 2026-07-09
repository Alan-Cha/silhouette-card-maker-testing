from __future__ import annotations

from plugins.abstraction_base.domain.Card import C
from plugins.abstraction_base.domain.Deck import Deck
from plugins.abstraction_base.application.DeckFormatPort import DeckFormatLike

class DeckFormat(DeckFormatLike[C]):

    def __init__(self, decklist_delimiter: str = '\n'):
        self.deck_splitter_delimiter = decklist_delimiter

    async def is_card_line_of_format(self, card_line: str):
        pass

    async def extract_card_data_from_card_line(self, card_line: str, index: int):
        pass

    async def parse_decklist(self, decklist: str):

        cards_of_deck: list[C] = []

        card_index = 0
        for line in decklist.strip().split(self.deck_splitter_delimiter):
            is_card_line = await self.is_card_line_of_format(line)
            if is_card_line:
                card_index += 1
                card_data = await self.extract_card_data_from_card_line(line, card_index)
                cards_of_deck.append(card_data)

        return Deck(cards=cards_of_deck)
