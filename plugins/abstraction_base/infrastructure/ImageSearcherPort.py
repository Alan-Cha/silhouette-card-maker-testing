from __future__ import annotations

from typing import Protocol, Optional

from plugins.abstraction_base.domain.Card import C
from plugins.abstraction_base.domain.CardImage import CardImage

class ImageSearcherLike(Protocol[C]):
	async def find_image(self, card: C) -> Optional[CardImage]:
		...
