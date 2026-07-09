from re import compile
from ast import literal_eval

from plugins.abstraction_base.application.DeckFormatAdapter import DeckFormat
from plugins.abstraction_base.domain.Card import Card
from plugins.abstraction_base.domain.Deck import Deck

class TTSDeckFormat(DeckFormat[Card]):

    PATTERN = compile(r'^([a-zA-Z0-9]+-\d+)$') # '{card code}'

    def __init__(self):
        super().__init__()

    async def is_card_line_of_format(self, card_line):
        return bool(self.PATTERN.match(card_line))

    async def extract_card_data_from_card_line(self, card_line, index):
        match = self.PATTERN.match(card_line)
        if match:
            card_code = match.group(1).strip()
            return Card(
                id = card_code,
                name = None,
                quantity = 1,
                placements = [index],
                front_image = None,
                back_image = None
            )
    
    async def parse_decklist(self, decklist):

        cards_of_deck: list[Card] = []

        card_index = 0
        for line in literal_eval(decklist.strip()):
            is_card_line = await self.is_card_line_of_format(line)
            if is_card_line:
                card_index += 1
                card_data = await self.extract_card_data_from_card_line(line, card_index)
                cards_of_deck.append(card_data)

        return Deck(cards=cards_of_deck)