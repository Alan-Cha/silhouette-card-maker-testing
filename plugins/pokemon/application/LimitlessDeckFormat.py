from re import compile

from plugins.abstraction_base.application.DeckFormatAdapter import DeckFormat
from plugins.pokemon.domain.PokemonCard import PokemonCard

class LimitlessDeckFormat(DeckFormat[PokemonCard]):

    PATTERN = compile(r'^(\d+)\s(.+)\s(\S+)\s(\S+)$') # '{Quantity} {Name} {Set} {Number}'

    def __init__(self):
        super().__init__()

    async def is_card_line_of_format(self, card_line):
        return bool(self.PATTERN.match(card_line))

    async def extract_card_data_from_card_line(self, card_line, index):
        match = self.PATTERN.match(card_line)
        if match:
            card_name = match.group(2).strip()
            quantity = int(match.group(1).strip())
            set_id = match.group(3).strip()
            card_number = match.group(4).strip()
            return PokemonCard(
                id = f'{set_id} {card_number}',
                name = card_name,
                quantity = quantity,
                placements = [index for _ in range(quantity)],
                front_image = None,
                back_image = None,
                set = set_id,
                card_number = card_number,
            )
    
    async def parse_decklist(self, decklist):
        return await super().parse_decklist(decklist)