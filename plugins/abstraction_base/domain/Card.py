from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, TypeVar, Optional

from plugins.abstraction_base.domain.CardImage import CardImage

class CardLike(Protocol):
    id: str
    name: str
    quantity: int
    placements: list[int]
    front_image: Optional[CardImage]
    back_image: Optional[CardImage]

@dataclass
class Card(CardLike):
    id: str
    name: str
    quantity: int
    placements: list[int]
    front_image: Optional[CardImage]
    back_image: Optional[CardImage]

C = TypeVar('C', bound=CardLike)

def card_placed_by_quantity(card: CardLike, quantity_supplied: int) -> Optional[int]:
    if 0 < quantity_supplied <= len(card.placements):
        return card.placements[quantity_supplied - 1]
    return None
