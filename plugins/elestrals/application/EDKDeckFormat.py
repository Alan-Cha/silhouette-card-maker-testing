from json import loads

from plugins.abstraction_base.application.DeckFormatAdapter import DeckFormat
from plugins.abstraction_base.domain.Card import Card
from plugins.abstraction_base.domain.Deck import Deck

class EDKDeckFormat(DeckFormat[Card]):

    def __init__(self):
        super().__init__()

    async def is_card_line_of_format(self, card_line):
        return bool(card_line.get('card'))

    async def extract_card_data_from_card_line(self, card_line, index):
        is_card_line = await self.is_card_line_of_format(card_line)
        if is_card_line:
            card_id = card_line.get('card')
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
        cards = data.get('mainDeck') + data.get('spiritDeck')

        card_index = 0
        for card in cards:
            is_card_line = await self.is_card_line_of_format(card)
            if is_card_line:
                card_index += 1
                card_data = await self.extract_card_data_from_card_line(card, card_index)
                cards_of_deck.append(card_data)
        
        return Deck(cards=cards_of_deck)