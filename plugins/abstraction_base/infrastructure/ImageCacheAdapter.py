from pathlib import Path

from plugins.abstraction_base.domain.CardImage import CardImage
from plugins.abstraction_base.infrastructure.ImageCachePort import ImageCacheLike, DEFAULT_IMAGE_CACHE_PATH, DEFAULT_IMAGE_CONTENT_TYPE
from plugins.abstraction_base.infrastructure.EnsurePath import EnsurePath

class ImageCacheAdapter(ImageCacheLike):

    def __init__(self, game: str):
        self.game = game

        image_cache_path = Path('.cache') / 'images'
        self.cache_path = image_cache_path / self.game

        EnsurePath(self.cache_path)

    async def get_cached_image_path_by_card_id(self, card_id: str) -> Path:
        return self.cache_path / DEFAULT_IMAGE_CACHE_PATH.format(CARD_ID=card_id)
    
    async def get_cached_image_path_by_filename(self, filename: str) -> Path:
        return self.cache_path / filename

    async def get_cached_image(self, card_id):
        cached_image_path = await self.get_cached_image_path_by_card_id(card_id)
        try:
            with open(cached_image_path, 'rb') as image_file:
                return CardImage(
                    filename=DEFAULT_IMAGE_CACHE_PATH.format(CARD_ID=card_id),
                    content_type=DEFAULT_IMAGE_CONTENT_TYPE,
                    data=image_file.read()
                )
        except FileNotFoundError:
            return None
    
    async def save_cached_image(self, image):
        if image != None:
            cached_image_path = await self.get_cached_image_path_by_filename(image.filename)
            with open(cached_image_path, 'wb') as image_file:
                image_file.write(image.data)