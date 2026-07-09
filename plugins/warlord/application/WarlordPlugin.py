from enum import Enum

from plugins.abstraction_base.application.GamePluginAdapter import GamePlugin
from plugins.warlord.application.UntapDeckFormat import UntapDeckFormat
from plugins.abstraction_base.infrastructure.CachedImageRepository import CachedImageRepository
from plugins.abstraction_base.infrastructure.ImageCacheAdapter import ImageCacheAdapter
from plugins.warlord.infrastructure.WarlordCCGDBImageSearcher import WarlordCCGDBImageSearcher
from plugins.abstraction_base.domain.Card import Card
from plugins.abstraction_base.domain.Deck import Deck

GAME_NAME = 'warlord'

class WarlordDeckFormats(Enum):
    UNTAP = 'untap'

class WarlordPlugin(GamePlugin):

    def __init__(self, format: WarlordDeckFormats):
        image_cache = ImageCacheAdapter(GAME_NAME)
        image_search = WarlordCCGDBImageSearcher()
        self.image_repository = CachedImageRepository(image_cache, image_search)
        
        match format:
            case WarlordDeckFormats.UNTAP:
                self.format = UntapDeckFormat()

    async def parse_deck(self, decklist):
        with open(decklist, 'r') as deck_file:
            deck_text = deck_file.read()
        return await super().parse_deck(deck_text)

    async def save_deck(self, deck):
        return await super().save_deck(deck)
