from enum import Enum

from plugins.abstraction_base.application.GamePluginAdapter import GamePlugin
from plugins.flesh_and_blood.application.FabraryDeckFormat import FabraryDeckFormat
from plugins.abstraction_base.infrastructure.CachedImageRepository import CachedImageRepository
from plugins.abstraction_base.infrastructure.ImageCacheAdapter import ImageCacheAdapter
from plugins.flesh_and_blood.infrastructure.FleshAndBloodImageSearcher import FleshAndBloodImageSearcher

GAME_NAME = 'flesh_and_blood'

class FleshAndBloodDeckFormats(Enum):
    FABRARY = 'fabrary'

class FleshAndBloodPlugin(GamePlugin):

    def __init__(self, format: FleshAndBloodDeckFormats):
        image_cache = ImageCacheAdapter(GAME_NAME)
        image_search = FleshAndBloodImageSearcher()
        self.image_repository = CachedImageRepository(image_cache, image_search)
        
        match format:
            case FleshAndBloodDeckFormats.FABRARY:
                self.format = FabraryDeckFormat()

    async def parse_deck(self, decklist):
        with open(decklist, 'r') as deck_file:
            deck_text = deck_file.read()
        return await super().parse_deck(deck_text)

    async def save_deck(self, deck):
        return await super().save_deck(deck)
