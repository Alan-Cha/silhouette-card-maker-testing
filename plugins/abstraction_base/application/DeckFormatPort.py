from __future__ import annotations

from typing import Protocol

from plugins.abstraction_base.domain.Card import C
from plugins.abstraction_base.domain.Deck import Deck

class DeckFormatLike(Protocol[C]):

    deck_splitter_delimiter: str

    def is_card_line_of_format(self, card_line: any) -> bool:
        ...

    def extract_card_data_from_card_line(self, card_line: any, index: int) -> C:
        ...

    def parse_decklist(self, decklist: str) -> Deck[C]:
        ...
