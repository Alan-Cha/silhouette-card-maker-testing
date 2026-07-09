from enum import Enum

from plugins.abstraction_base.application.GamePluginAdapter import GamePlugin
from plugins.pokemon.application.LimitlessDeckFormat import LimitlessDeckFormat
from plugins.abstraction_base.infrastructure.CachedImageRepository import CachedImageRepository
from plugins.abstraction_base.infrastructure.ImageCacheAdapter import ImageCacheAdapter
from plugins.pokemon.infrastructure.PokemonImageSearcher import PokemonImageSearcher

GAME_NAME = 'pokemon'

class PokemonDeckFormats(Enum):
    LIMITLESS = 'limitless'

class PokemonPlugin(GamePlugin):

    def __init__(self, format: PokemonDeckFormats):
        image_cache = ImageCacheAdapter(GAME_NAME)
        image_search = PokemonImageSearcher()
        self.image_repository = CachedImageRepository(image_cache, image_search)
        
        match format:
            case PokemonDeckFormats.LIMITLESS:
                self.format = LimitlessDeckFormat()

    async def parse_deck(self, decklist):
        with open(decklist, 'r') as deck_file:
            deck_text = deck_file.read()
        return await super().parse_deck(deck_text)

    async def save_deck(self, deck):
        return await super().save_deck(deck)
