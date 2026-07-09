from re import compile, sub, IGNORECASE

from plugins.abstraction_base.application.DeckFormatAdapter import DeckFormat
from plugins.lorcana.domain.LorcanaCard import LorcanaCard

class DreambornDeckFormat(DeckFormat[LorcanaCard]):

    PATTERN = compile(r'(\d+)x?\s+(.+)', IGNORECASE) # '{Quantity} {Name}' or '{Quantity}x {Name}'

    def __init__(self):
        super().__init__()

    async def is_card_line_of_format(self, card_line):
        return bool(self.PATTERN.match(card_line))

    async def remove_nonalphanumeric(self, s: str) -> str:
        return sub(r'[^\w]', '', s)

    async def extract_card_data_from_card_line(self, card_line, index):
        match = self.PATTERN.match(card_line)
        if match:
            card_quantity = int(match.group(1))
            enchanted = False
            card_name = match.group(2).strip()

            if "*E*" in card_name:
                enchanted = True
                card_name = card_name.replace('*E*','')

            clean_card_name = await self.remove_nonalphanumeric(card_name)

            return LorcanaCard(
                id = card_name,
                clean_name = clean_card_name,
                name = card_name,
                quantity = card_quantity,
                placements = [index for _ in range(card_quantity)],
                front_image = None,
                back_image = None,
                enchanted = enchanted
            )
    
    async def parse_decklist(self, decklist):
        return await super().parse_decklist(decklist)