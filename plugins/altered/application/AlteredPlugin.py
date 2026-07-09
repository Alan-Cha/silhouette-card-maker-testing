from enum import Enum

from plugins.abstraction_base.application.GamePluginAdapter import GamePlugin
from plugins.altered.application.AjordatDeckFormat import AjordatDeckFormat
from plugins.abstraction_base.infrastructure.CachedImageRepository import CachedImageRepository
from plugins.abstraction_base.infrastructure.ImageCacheAdapter import ImageCacheAdapter
from plugins.altered.infrastructure.AlteredImageSearcher import AlteredImageSearcher

GAME_NAME = 'altered'

class AlteredDeckFormats(Enum):
    AJORDAT = 'ajordat'

class AlteredPlugin(GamePlugin):

    def __init__(self, format: AlteredDeckFormats):
        image_cache = ImageCacheAdapter(GAME_NAME)
        image_search = AlteredImageSearcher()
        self.image_repository = CachedImageRepository(image_cache, image_search)
        
        match format:
            case AlteredDeckFormats.AJORDAT:
                self.format = AjordatDeckFormat()

    async def parse_deck(self, decklist):
        with open(decklist, 'r') as deck_file:
            deck_text = deck_file.read()
        return await super().parse_deck(deck_text)

    async def save_deck(self, deck):
        return await super().save_deck(deck)
