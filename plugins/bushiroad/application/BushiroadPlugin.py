from enum import Enum
from pathlib import Path

from plugins.abstraction_base.application.GamePluginAdapter import GamePlugin
from plugins.abstraction_base.infrastructure.CachedImageRepository import CachedImageRepository
from plugins.abstraction_base.infrastructure.ImageCacheAdapter import ImageCacheAdapter
from plugins.bushiroad.infrastructure.BushiroadImageSearcher import BushiroadImageSearcher
from plugins.bushiroad.application.BushiroadURLDeckFormat import BushiroadURLDeckFormat

GAME_NAME = 'bushiroad'

class BushiroadDeckFormats(Enum):
    BUSHIROAD_URL = 'bushiroad_url'

URL_DECK_FORMATS = [ BushiroadDeckFormats.BUSHIROAD_URL ]

class BushiroadPlugin(GamePlugin):

    is_url_format: bool = False

    def __init__(self, format: BushiroadDeckFormats):
        image_cache = ImageCacheAdapter(GAME_NAME)
        image_search = BushiroadImageSearcher()
        self.image_repository = CachedImageRepository(image_cache, image_search)
        
        match format:
            case BushiroadDeckFormats.BUSHIROAD_URL:
                self.format = BushiroadURLDeckFormat()
        
        self.is_url_format = format in URL_DECK_FORMATS

    async def parse_deck(self, decklist):
        is_decklist_a_file: bool = Path(decklist).exists()
        
        if self.is_url_format and not is_decklist_a_file:
            deck_text = decklist
        else:
            with open(decklist, 'r') as deck_file:
                deck_text = deck_file.read()
        return await super().parse_deck(deck_text)

    async def save_deck(self, deck):
        return await super().save_deck(deck)
