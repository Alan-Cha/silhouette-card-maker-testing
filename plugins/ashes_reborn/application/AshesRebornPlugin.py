from enum import Enum
from pathlib import Path

from plugins.abstraction_base.application.GamePluginAdapter import GamePlugin
from plugins.abstraction_base.infrastructure.CachedImageRepository import CachedImageRepository
from plugins.abstraction_base.infrastructure.ImageCacheAdapter import ImageCacheAdapter
from plugins.ashes_reborn.infrastructure.AshesImageSearcher import AshesImageSearcher
from plugins.ashes_reborn.infrastructure.AshesDBImageSearcher import AshesDBImageSearcher
from plugins.ashes_reborn.application.AshesURLDeckFormat import AshesURLDeckFormat
from plugins.ashes_reborn.application.AshesDBURLDeckFormat import AshesDBURLDeckFormat
from plugins.ashes_reborn.domain.ImageServerSource import ImageServerSource

GAME_NAME = 'ashes_reborn'

class AshesRebornDeckFormats(Enum):
    ASHESDB_URL = 'ashesdb_share_url'
    ASHES_URL   = 'ashes_share_url'

URL_DECK_FORMATS = [ AshesRebornDeckFormats.ASHESDB_URL, AshesRebornDeckFormats.ASHES_URL ]

class AshesRebornPlugin(GamePlugin):

    is_url_format: bool = False

    def __init__(self, format: AshesRebornDeckFormats, image_server: ImageServerSource):
        image_cache = ImageCacheAdapter(GAME_NAME)

        match image_server:
            case ImageServerSource.ASHES:
                image_search = AshesImageSearcher()
            case ImageServerSource.ASHESDB:
                image_search = AshesDBImageSearcher()
        self.image_repository = CachedImageRepository(image_cache, image_search)
        
        match format:
            case AshesRebornDeckFormats.ASHESDB_URL:
                self.format = AshesDBURLDeckFormat()
            case AshesRebornDeckFormats.ASHES_URL:
                self.format = AshesURLDeckFormat()
        
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
