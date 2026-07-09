from enum import Enum

from plugins.abstraction_base.application.GamePluginAdapter import GamePlugin
from plugins.elestrals.application.EDKDeckFormat import EDKDeckFormat
from plugins.abstraction_base.infrastructure.CachedImageRepository import CachedImageRepository
from plugins.abstraction_base.infrastructure.ImageCacheAdapter import ImageCacheAdapter
from plugins.elestrals.infrastructure.ElestralsImageSearcher import ElestralsImageSearcher

GAME_NAME = 'elestrals'

class ElestralsDeckFormats(Enum):
    EDK = 'edk'

class ElestralsPlugin(GamePlugin):

    def __init__(self, format: ElestralsDeckFormats):
        image_cache = ImageCacheAdapter(GAME_NAME)
        image_search = ElestralsImageSearcher()
        self.image_repository = CachedImageRepository(image_cache, image_search)
        
        match format:
            case ElestralsDeckFormats.EDK:
                self.format = EDKDeckFormat()

    async def parse_deck(self, decklist):
        with open(decklist, 'r') as deck_file:
            deck_text = deck_file.read()
        return await super().parse_deck(deck_text)

    async def save_deck(self, deck):
        return await super().save_deck(deck)
