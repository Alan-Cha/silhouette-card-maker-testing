from json import loads
from re import compile

from plugins.abstraction_base.application.DeckFormatAdapter import DeckFormat
from plugins.abstraction_base.domain.Card import Card
from plugins.abstraction_base.domain.Deck import Deck

class JSONDeckFormat(DeckFormat[Card]):

    PATTERN = compile(r'.+-.+') # 'SET-NUMBER'

    def __init__(self):
        super().__init__()

    async def is_card_line_of_format(self, card_line):
        return bool(self.PATTERN.match(card_line))

    async def extract_card_data_from_card_line(self, card_line, index):
        match = self.PATTERN.match(card_line)
        if match:
            card_id = card_line
            return Card(
                id = card_id,
                name = None,
                quantity = 1,
                placements = [index],
                front_image = None,
                back_image = None
            )
    
    async def parse_decklist(self, decklist):
        cards_of_deck = []

        data = loads(decklist)
        card_areas = data.get('zones')

        card_index = 0
        for area in card_areas:
            for card in card_areas.get(area):
                is_card_line = await self.is_card_line_of_format(card)
                if is_card_line:
                    card_index += 1
                    card_data = await self.extract_card_data_from_card_line(card, card_index)
                    cards_of_deck.append(card_data)

        return Deck(cards=cards_of_deck)