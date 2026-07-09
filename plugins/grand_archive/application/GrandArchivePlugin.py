from enum import Enum

from plugins.abstraction_base.application.GamePluginAdapter import GamePlugin
from plugins.grand_archive.application.OmnideckDeckFormat import OmnideckDeckFormat
from plugins.abstraction_base.infrastructure.CachedImageRepository import CachedImageRepository
from plugins.abstraction_base.infrastructure.ImageCacheAdapter import ImageCacheAdapter
from plugins.grand_archive.infrastructure.GrandArchiveImageSearcher import GrandArchiveImageSearcher

GAME_NAME = 'grand_archive'

class GrandArchiveDeckFormats(Enum):
    OMNIDECK = 'omnideck'

class GrandArchivePlugin(GamePlugin):

    def __init__(self, format: GrandArchiveDeckFormats):
        image_cache = ImageCacheAdapter(GAME_NAME)
        image_search = GrandArchiveImageSearcher()
        self.image_repository = CachedImageRepository(image_cache, image_search)
        
        match format:
            case GrandArchiveDeckFormats.OMNIDECK:
                self.format = OmnideckDeckFormat()

    async def parse_deck(self, decklist):
        with open(decklist, 'r') as deck_file:
            deck_text = deck_file.read()
        return await super().parse_deck(deck_text)

    async def save_deck(self, deck):
        return await super().save_deck(deck)
