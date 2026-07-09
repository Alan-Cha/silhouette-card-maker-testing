from __future__ import annotations

from pathlib import Path
from typing import Protocol, Optional

from plugins.abstraction_base.domain.CardImage import CardImage

DEFAULT_IMAGE_CACHE_PATH = '{CARD_ID}.png'
DEFAULT_IMAGE_CONTENT_TYPE = 'image/png'
DEFAULT_IMAGE_FORMAT = 'PNG'

class ImageCacheLike(Protocol):

	game: str
	cache_path: Path

	async def get_cached_image(self, card_id: str) -> Optional[CardImage]:
		...

	async def save_cached_image(self, image: CardImage) -> None:
		...
		