from enum import Enum

from plugins.abstraction_base.application.GamePluginAdapter import GamePlugin
from plugins.lorcana.application.DreambornDeckFormat import DreambornDeckFormat
from plugins.abstraction_base.infrastructure.CachedImageRepository import CachedImageRepository
from plugins.abstraction_base.infrastructure.ImageCacheAdapter import ImageCacheAdapter
from plugins.lorcana.infrastructure.LorcastImageSearcher import LorcastImageSearcher

GAME_NAME = 'lorcana'

class LorcanaDeckFormats(Enum):
    DREAMBORN = 'dreamborn'

class LorcanaPlugin(GamePlugin):

    def __init__(self, format: LorcanaDeckFormats):
        image_cache = ImageCacheAdapter(GAME_NAME)
        image_search = LorcastImageSearcher()
        self.image_repository = CachedImageRepository(image_cache, image_search)
        
        match format:
            case LorcanaDeckFormats.DREAMBORN:
                self.format = DreambornDeckFormat()

    async def parse_deck(self, decklist):
        with open(decklist, 'r') as deck_file:
            deck_text = deck_file.read()
        return await super().parse_deck(deck_text)

    async def save_deck(self, deck):
        return await super().save_deck(deck)
