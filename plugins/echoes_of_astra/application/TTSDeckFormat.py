from json import loads

from plugins.abstraction_base.application.DeckFormatAdapter import DeckFormat
from plugins.abstraction_base.domain.Card import Card
from plugins.abstraction_base.domain.Deck import Deck

class TTSDeckFormat(DeckFormat[Card]):

    def __init__(self):
        super().__init__()

    async def is_card_line_of_format(self, card_line):
        return bool(card_line.get('count') and card_line.get('name'))

    async def extract_card_data_from_card_line(self, card_line, index):
        match = await self.is_card_line_of_format(card_line)
        if match:
            card_name = card_line.get('name')
            card_quantity = card_line.get('count')
            return Card(
                id = card_name,
                name = card_name,
                quantity = card_quantity,
                placements = [index for _ in range(card_quantity)],
                front_image = None,
                back_image = None
            )
    
    async def parse_decklist(self, decklist):
        cards_of_deck = []

        cards = loads(decklist)

        card_index = 0
        for card in cards:
            is_card_line = await self.is_card_line_of_format(card)
            if is_card_line:
                card_index += 1
                card_data = await self.extract_card_data_from_card_line(card, card_index)
                cards_of_deck.append(card_data)
        
        return Deck(cards=cards_of_deck)