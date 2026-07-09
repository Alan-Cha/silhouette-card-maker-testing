from re import compile

from plugins.abstraction_base.application.DeckFormatAdapter import DeckFormat
from plugins.flesh_and_blood.domain.FleshAndBloodCard import FleshAndBloodCard
from plugins.flesh_and_blood.domain.Pitch import Pitch
from plugins.flesh_and_blood.application.GetCardID import get_card_id

class FabraryDeckFormat(DeckFormat[FleshAndBloodCard]):

    PATTERN = compile(r'(\d+)x\s+([^(]+?)(?:\s+\((red|yellow|blue)\))?$') # '{quantity}x {name} {pitch?}' where pitch is optional

    def __init__(self):
        super().__init__()

    async def is_card_line_of_format(self, card_line):
        return bool(self.PATTERN.match(card_line))

    async def extract_card_data_from_card_line(self, card_line, index):
        match = self.PATTERN.match(card_line)
        if match:
            quantity = int(match.group(1).strip())
            name = match.group(2).strip()
            pitch_extract = '' if match.group(3) is None else match.group(3).strip()
            if pitch_extract == 'red':
                pitch = Pitch.RED
            elif pitch_extract == 'yellow':
                pitch = Pitch.YELLOW
            elif pitch_extract == 'blue':
                pitch = Pitch.BLUE
            else:
                pitch = Pitch.NONE
            card_id = await get_card_id(name, pitch)
            return FleshAndBloodCard(
                id = card_id,
                name = name,
                quantity = quantity,
                placements = [index for _ in range(quantity)],
                front_image = None,
                back_image = None,
                pitch = pitch
            )
    
    async def parse_decklist(self, decklist):
        return await super().parse_decklist(decklist)