from enum import Enum

from plugins.abstraction_base.application.GamePluginAdapter import GamePlugin
from plugins.cyberpunk.application.LimitlessDeckFormat import LimitlessDeckFormat
from plugins.abstraction_base.infrastructure.CachedImageRepository import CachedImageRepository
from plugins.abstraction_base.infrastructure.ImageCacheAdapter import ImageCacheAdapter
from plugins.cyberpunk.infrastructure.CyberpunkImageSearcher import CyberpunkImageSearcher

GAME_NAME = 'cyberpunk'

class CyberpunkDeckFormats(Enum):
    LIMITLESS = 'limitless'

class CyberpunkPlugin(GamePlugin):

    def __init__(self, format: CyberpunkDeckFormats):
        image_cache = ImageCacheAdapter(GAME_NAME)
        image_search = CyberpunkImageSearcher()
        self.image_repository = CachedImageRepository(image_cache, image_search)
        
        match format:
            case CyberpunkDeckFormats.LIMITLESS:
                self.format = LimitlessDeckFormat()

    async def parse_deck(self, decklist):
        with open(decklist, 'r') as deck_file:
            deck_text = deck_file.read()
        return await super().parse_deck(deck_text)

    async def save_deck(self, deck):
        return await super().save_deck(deck)
