from __future__ import annotations

from typing import Protocol
from types import CodeType

from plugins.abstraction_base.domain.Card import C
from plugins.abstraction_base.domain.Deck import Deck

class DeckSearcherLike(Protocol[C]):

    URL_PATTERN: CodeType
    API_TEMPLATE: str

    async def is_url_for_deck(self, deck_url: str) -> bool:
        ...
    
    async def extract_deck_from_url(self, deck_url: str) -> Deck[C]:
        ...
