from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from plugins.abstraction_base.domain.Card import CardLike
from plugins.abstraction_base.domain.CardImage import CardImage
from plugins.bushiroad.domain.BushiroadGame import BushiroadGameTitle

@dataclass
class BushiroadCard(CardLike):
    id: str
    name: str
    quantity: int
    placements: list[int]
    front_image: Optional[CardImage]
    back_image: Optional[CardImage]
    bushiroad_game: BushiroadGameTitle
    front_image_url: str
    back_image_url: Optional[str]