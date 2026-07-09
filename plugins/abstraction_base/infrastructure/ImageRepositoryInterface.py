from __future__ import annotations

from typing import Protocol, Optional

from plugins.abstraction_base.domain.Card import C
from plugins.abstraction_base.infrastructure.ImageCachePort import ImageCacheLike
from plugins.abstraction_base.infrastructure.ImageSearcherPort import ImageSearcherLike

class ImageRepositoryLike(Protocol[C]):

	_cache: ImageCacheLike
	_searcher: ImageSearcherLike[C]

	async def get_image(self, card: C) -> Optional[C]:
		...

	async def save_image(self, card: C) -> None:
		...
