from enum import Enum

from plugins.abstraction_base.application.GamePluginAdapter import GamePlugin
from plugins.neuroscape.application.DeckPlanetDeckFormat import DeckPlanetDeckFormat
from plugins.neuroscape.application.DeckscapeDeckFormat import DeckscapeDeckFormat
from plugins.abstraction_base.infrastructure.CachedImageRepository import CachedImageRepository
from plugins.abstraction_base.infrastructure.ImageCacheAdapter import ImageCacheAdapter
from plugins.neuroscape.infrastructure.NeuroscapeImageSearcher import NeuroscapeImageSearcher

GAME_NAME = 'neuroscape'

class NeuroscapeDeckFormats(Enum):
    DECKPLANET = 'deckplanet'
    DECKSCAPE  = 'deckscape'

class NeuroscapePlugin(GamePlugin):

    def __init__(self, format: NeuroscapeDeckFormats):
        image_cache = ImageCacheAdapter(GAME_NAME)
        image_search = NeuroscapeImageSearcher()
        self.image_repository = CachedImageRepository(image_cache, image_search)
        
        match format:
            case NeuroscapeDeckFormats.DECKPLANET:
                self.format = DeckPlanetDeckFormat()
            case NeuroscapeDeckFormats.DECKSCAPE:
                self.format = DeckscapeDeckFormat()

    async def parse_deck(self, decklist):
        with open(decklist, 'r') as deck_file:
            deck_text = deck_file.read()
        return await super().parse_deck(deck_text)

    async def save_deck(self, deck):
        return await super().save_deck(deck)
