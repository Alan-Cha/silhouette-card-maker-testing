from enum import Enum
from pathlib import Path

from plugins.abstraction_base.application.GamePluginAdapter import GamePlugin
from plugins.abstraction_base.infrastructure.CachedImageRepository import CachedImageRepository
from plugins.abstraction_base.infrastructure.ImageCacheAdapter import ImageCacheAdapter
from plugins.cookie_run_braverse.infrastructure.CookieRunImageSearcher import CookieRunImageSearcher
from plugins.cookie_run_braverse.application.CookieRunTCGDeckFormat import CookieRunTCGDeckFormat

GAME_NAME = 'cookie_run_braverse'

class CookieRunDeckFormats(Enum):
    COOKIERUNTCG_URL = 'cookieruntcg_url'

URL_DECK_FORMATS = [ CookieRunDeckFormats.COOKIERUNTCG_URL ]

class CookieRunPlugin(GamePlugin):

    is_url_format: bool = False

    def __init__(self, format: CookieRunDeckFormats):
        image_cache = ImageCacheAdapter(GAME_NAME)
        image_search = CookieRunImageSearcher()
        self.image_repository = CachedImageRepository(image_cache, image_search)
        
        match format:
            case CookieRunDeckFormats.COOKIERUNTCG_URL:
                self.format = CookieRunTCGDeckFormat()
        
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
