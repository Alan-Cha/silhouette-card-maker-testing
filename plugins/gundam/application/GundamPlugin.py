from enum import Enum

from plugins.abstraction_base.application.GamePluginAdapter import GamePlugin
from plugins.gundam.application.LimitlessDeckFormat import LimitlessDeckFormat
from plugins.gundam.application.DeckPlanetDeckFormat import DeckPlanetDeckFormat
from plugins.gundam.application.EgmanDeckFormat import EgmanDeckFormat
from plugins.gundam.application.ExBurstDeckFormat import ExBurstDeckFormat
from plugins.abstraction_base.infrastructure.CachedImageRepository import CachedImageRepository
from plugins.abstraction_base.infrastructure.ImageCacheAdapter import ImageCacheAdapter
from plugins.gundam.infrastructure.BandaiImageSearcher import BandaiImageSearcher

GAME_NAME = 'gundam'

class GundamDeckFormats(Enum):
    DECKPLANET = 'deckplanet'
    EGMAN      = 'egman'
    EXBURST    = 'exburst'
    LIMITLESS  = 'limitless'

class GundamPlugin(GamePlugin):

    def __init__(self, format: GundamDeckFormats):
        image_cache = ImageCacheAdapter(GAME_NAME)
        image_search = BandaiImageSearcher()
        self.image_repository = CachedImageRepository(image_cache, image_search)
        
        match format:
            case GundamDeckFormats.DECKPLANET:
                self.format = DeckPlanetDeckFormat()
            case GundamDeckFormats.EGMAN:
                self.format = EgmanDeckFormat()
            case GundamDeckFormats.EXBURST:
                self.format = ExBurstDeckFormat()
            case GundamDeckFormats.LIMITLESS:
                self.format = LimitlessDeckFormat()

    async def parse_deck(self, decklist):
        with open(decklist, 'r') as deck_file:
            deck_text = deck_file.read()
        return await super().parse_deck(deck_text)

    async def save_deck(self, deck):
        return await super().save_deck(deck)
