from enum import Enum
from pathlib import Path

from plugins.abstraction_base.application.GamePluginAdapter import GamePlugin
from plugins.abstraction_base.infrastructure.CachedImageRepository import CachedImageRepository
from plugins.abstraction_base.infrastructure.ImageCacheAdapter import ImageCacheAdapter
from plugins.chrono_core.infrastructure.ChronoCoreImageSearcher import ChronoCoreImageSearcher
from plugins.chrono_core.application.SleevedURLDeckFormat import SleevedURLDeckFormat
from plugins.chrono_core.application.TextDeckFormat import TextDeckFormat
from plugins.chrono_core.application.JSONDeckFormat import JSONDeckFormat

GAME_NAME = 'chrono_core'

class ChronoCoreDeckFormats(Enum):
    SLEEVED_URL = 'sleeved_url'
    TEXT        = 'text'
    JSON        = 'json'

URL_DECK_FORMATS = [ ChronoCoreDeckFormats.SLEEVED_URL ]

class ChronoCorePlugin(GamePlugin):

    is_url_format: bool = False

    def __init__(self, format: ChronoCoreDeckFormats):
        image_cache = ImageCacheAdapter(GAME_NAME)
        image_search = ChronoCoreImageSearcher()
        self.image_repository = CachedImageRepository(image_cache, image_search)
        
        match format:
            case ChronoCoreDeckFormats.SLEEVED_URL:
                self.format = SleevedURLDeckFormat()
            case ChronoCoreDeckFormats.TEXT:
                self.format = TextDeckFormat()
            case ChronoCoreDeckFormats.JSON:
                self.format = JSONDeckFormat()
        
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
