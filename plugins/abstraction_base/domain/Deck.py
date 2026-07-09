from __future__ import annotations

from dataclasses import dataclass
from typing import Generic

from plugins.abstraction_base.domain.Card import C

@dataclass
class Deck(Generic[C]):
	cards: list[C]
