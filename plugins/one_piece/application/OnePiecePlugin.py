from enum import Enum

from plugins.abstraction_base.application.GamePluginAdapter import GamePlugin
from plugins.one_piece.application.EgmanDeckFormat import EgmanDeckFormat
from plugins.one_piece.application.OPTCGSimDeckFormat import OPTCGSimDeckFormat
from plugins.abstraction_base.infrastructure.CachedImageRepository import CachedImageRepository
from plugins.abstraction_base.infrastructure.ImageCacheAdapter import ImageCacheAdapter
from plugins.one_piece.infrastructure.BandaiImageSearcher import BandaiImageSearcher

GAME_NAME = 'one_piece'

class OnePieceDeckFormats(Enum):
    EGMAN    = 'egman'
    OPTCGSIM = 'optcgsim'

class OnePiecePlugin(GamePlugin):

    def __init__(self, format: OnePieceDeckFormats):
        image_cache = ImageCacheAdapter(GAME_NAME)
        image_search = BandaiImageSearcher()
        self.image_repository = CachedImageRepository(image_cache, image_search)
        
        match format:
            case OnePieceDeckFormats.EGMAN:
                self.format = EgmanDeckFormat()
            case OnePieceDeckFormats.OPTCGSIM:
                self.format = OPTCGSimDeckFormat()

    async def parse_deck(self, decklist):
        with open(decklist, 'r') as deck_file:
            deck_text = deck_file.read()
        return await super().parse_deck(deck_text)

    async def save_deck(self, deck):
        return await super().save_deck(deck)
    
    async def get_card_images_for_deck(self, deck):
        return await super().get_card_images_for_deck(deck)