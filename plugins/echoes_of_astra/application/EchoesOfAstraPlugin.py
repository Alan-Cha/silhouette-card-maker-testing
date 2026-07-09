from enum import Enum

from plugins.abstraction_base.application.GamePluginAdapter import GamePlugin
from plugins.echoes_of_astra.application.TTSDeckFormat import TTSDeckFormat
from plugins.echoes_of_astra.application.TextDeckFormat import TextDeckFormat
from plugins.abstraction_base.infrastructure.CachedImageRepository import CachedImageRepository
from plugins.abstraction_base.infrastructure.ImageCacheAdapter import ImageCacheAdapter
from plugins.echoes_of_astra.infrastructure.EchoesOfAstraImageSearcher import EchoesOfAstraImageSearcher

GAME_NAME = 'echoes_of_astra'

class EchoesOfAstraDeckFormats(Enum):
    TABLETOP_SIMULATOR = 'tts'
    TEXT               = 'text'

class EchoesOfAstraPlugin(GamePlugin):

    def __init__(self, format: EchoesOfAstraDeckFormats):
        image_cache = ImageCacheAdapter(GAME_NAME)
        image_search = EchoesOfAstraImageSearcher()
        self.image_repository = CachedImageRepository(image_cache, image_search)
        
        match format:
            case EchoesOfAstraDeckFormats.TABLETOP_SIMULATOR:
                self.format = TTSDeckFormat()
            case EchoesOfAstraDeckFormats.TEXT:
                self.format = TextDeckFormat()

    async def parse_deck(self, decklist):
        with open(decklist, 'r') as deck_file:
            deck_text = deck_file.read()
        return await super().parse_deck(deck_text)

    async def save_deck(self, deck):
        return await super().save_deck(deck)
