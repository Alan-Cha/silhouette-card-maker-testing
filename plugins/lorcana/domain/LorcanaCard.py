from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from plugins.abstraction_base.domain.Card import CardLike
from plugins.abstraction_base.domain.CardImage import CardImage

@dataclass
class LorcanaCard(CardLike):
    id: str
    clean_name: str
    name: str
    quantity: int
    placements: list[int]
    front_image: Optional[CardImage]
    back_image: Optional[CardImage]
    enchanted: bool