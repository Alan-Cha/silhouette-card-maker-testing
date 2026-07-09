from re import compile

from plugins.abstraction_base.application.DeckFormatAdapter import DeckFormat
from plugins.riftbound.domain.RiftboundCard import RiftboundCard

class TTSDeckFormat(DeckFormat[RiftboundCard]):

    PATTERN = compile(r'^([A-Z0-9]+)-(\d+[a-z]?)-(\d+)$') # '{Set ID}-{Card ID}-{Art Number}'
    ALTERNATE_ART_SUFFIX = 'a'

    def __init__(self):
        super().__init__(' ')

    async def is_card_line_of_format(self, card_line):
        return bool(self.PATTERN.match(card_line))

    async def extract_card_data_from_card_line(self, card_line, index):
        match = self.PATTERN.match(card_line)
        if match:
            card_number = f'{ match.group(1).strip() }-{ match.group(2).strip() }'

            if int(match.group(3)) > 1:
                card_number = f'{card_number}{self.ALTERNATE_ART_SUFFIX}' # Assume that the desired art is the alternate art

            return RiftboundCard(
                id = card_number,
                name = None,
                quantity = 1,
                placements = [index],
                front_image = None,
                back_image = None,
                card_number = card_number,
            )
    
    async def parse_decklist(self, decklist):
        return await super().parse_decklist(decklist)