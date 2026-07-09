from re import compile

from plugins.abstraction_base.application.DeckFormatAdapter import DeckFormat
from plugins.abstraction_base.domain.Card import Card

class EgmanDeckFormat(DeckFormat[Card]):

    PATTERN = compile(r'^(\d+)\s+([A-Z0-9]+-\d+)\s+([^|]+)')  # '{Quantity} {Card Number} {Name}'

    def __init__(self):
        super().__init__()

    async def is_card_line_of_format(self, card_line):
        return bool(self.PATTERN.match(card_line))

    async def extract_card_data_from_card_line(self, card_line, index):
        match = self.PATTERN.match(card_line)
        if match:
            quantity = int(match.group(1).strip())
            card_code = match.group(2).strip()
            name = match.group(3).strip()

            return Card(
                id = card_code,
                name = name,
                quantity = quantity,
                placements = [index for _ in range(quantity)],
                front_image = None,
                back_image = None,
            )
    
    async def parse_decklist(self, decklist):
        return await super().parse_decklist(decklist)