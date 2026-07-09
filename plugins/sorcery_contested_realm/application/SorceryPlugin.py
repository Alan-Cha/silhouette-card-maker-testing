from enum import Enum
from pathlib import Path

from plugins.abstraction_base.application.GamePluginAdapter import GamePlugin
from plugins.abstraction_base.infrastructure.CachedImageRepository import CachedImageRepository
from plugins.abstraction_base.infrastructure.ImageCacheAdapter import ImageCacheAdapter
from plugins.sorcery_contested_realm.infrastructure.CuriosaImageSearcher import CuriosaImageSearcher
from plugins.sorcery_contested_realm.application.CuriosaDeckFormat import CuriosaDeckFormat

GAME_NAME = 'sorcery_contested_realm'

class SorceryDeckFormats(Enum):
    CURIOSA_URL = 'curiosa_url'

URL_DECK_FORMATS = [ SorceryDeckFormats.CURIOSA_URL ]

class SorceryPlugin(GamePlugin):

    is_url_format: bool = False

    def __init__(self, format: SorceryDeckFormats):
        image_cache = ImageCacheAdapter(GAME_NAME)
        image_search = CuriosaImageSearcher()
        self.image_repository = CachedImageRepository(image_cache, image_search)
        
        match format:
            case SorceryDeckFormats.CURIOSA_URL:
                self.format = CuriosaDeckFormat()
        
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
