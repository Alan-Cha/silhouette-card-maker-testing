from pathlib import Path

from plugins.abstraction_base.domain.Card import Card, card_placed_by_quantity
from plugins.abstraction_base.infrastructure.ImageRepositoryInterface import ImageRepositoryLike
from plugins.abstraction_base.infrastructure.ImageCachePort import ImageCacheLike
from plugins.abstraction_base.infrastructure.ImageSearcherPort import ImageSearcherLike
from plugins.abstraction_base.infrastructure.EnsurePath import EnsurePath

class CachedImageRepository(ImageRepositoryLike[Card]):
	def __init__(self, cache: ImageCacheLike, searcher: ImageSearcherLike[Card]) -> None:
		self._cache = cache
		self._searcher = searcher

	async def get_image(self, card):
		cached = await self._cache.get_cached_image(card.id)
		if cached is not None:
			return cached

		found = await self._searcher.find_image(card)
		if found is None:
			return None

		await self._cache.save_cached_image(found)
		return found

	def save_image(self, card):
		image_path = Path('game')
		front_path = image_path / 'front'
		back_path = image_path / 'double_sided'

		EnsurePath(front_path)
		EnsurePath(back_path)
		
		for index in range(card.quantity):

			if card.front_image != None:
				index_path = f'{card_placed_by_quantity(card, index+1)}_{index}_{card.front_image.filename}'
				with open(front_path / index_path, 'wb') as image_file:
					image_file.write(card.front_image.data)

			if card.back_image != None:
				index_path = f'{card_placed_by_quantity(card, index+1)}_{index}_{card.back_image.filename}'
				with open(back_path / index_path, 'wb') as image_file:
					image_file.write(card.back_image.data)
