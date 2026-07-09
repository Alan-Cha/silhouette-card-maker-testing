from re import compile

from plugins.abstraction_base.application.DeckFormatAdapter import DeckFormat
from plugins.riftbound.domain.RiftboundCard import RiftboundCard

class PiltoverArchiveDeckFormat(DeckFormat[RiftboundCard]):

    PATTERN = compile(r'^(\d+) (.+)$') # '{Quantity} {Card Name}'

    def __init__(self):
        super().__init__()

    async def is_card_line_of_format(self, card_line):
        return bool(self.PATTERN.match(card_line))

    async def extract_card_data_from_card_line(self, card_line, index):
        match = self.PATTERN.match(card_line)
        if match:
            quantity = int(match.group(1))
            name = match.group(2)

            return RiftboundCard(
                id = name,
                name = name,
                quantity = quantity,
                placements = [index for _ in range(quantity)],
                front_image = None,
                back_image = None,
                card_number = None,
            )
    
    async def parse_decklist(self, decklist):
        return await super().parse_decklist(decklist)