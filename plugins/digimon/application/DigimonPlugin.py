from enum import Enum

from plugins.abstraction_base.application.GamePluginAdapter import GamePlugin
from plugins.digimon.application.DigimonCardAppDeckFormat import DigimonCardAppDeckFormat
from plugins.digimon.application.DigimonCardDevDeckFormat import DigimonCardDevDeckFormat
from plugins.digimon.application.DigimonCardIODeckFormat import DigimonCardIODeckFormat
from plugins.digimon.application.DigimonMetaDeckFormat import DigimonMetaDeckFormat
from plugins.digimon.application.TTSDeckFormat import TTSDeckFormat
from plugins.digimon.application.UntapDeckFormat import UntapDeckFormat
from plugins.abstraction_base.infrastructure.CachedImageRepository import CachedImageRepository
from plugins.abstraction_base.infrastructure.ImageCacheAdapter import ImageCacheAdapter
from plugins.digimon.infrastructure.BandaiImageSearcher import BandaiImageSearcher

GAME_NAME = 'digimon'

class DigimonDeckFormats(Enum):
    DIGIMONCARDAPP     = 'digimoncardapp'
    DIGIMONCARDDEV     = 'digimoncarddev'
    DIGIMONCARDIO      = 'digimoncardio'
    DIGIMONMETA        = 'digimonmeta'
    TABLETOP_SIMULATOR = 'tts'
    UNTAP              = 'untap'


class DigimonPlugin(GamePlugin):

    def __init__(self, format: DigimonDeckFormats):
        image_cache = ImageCacheAdapter(GAME_NAME)
        image_search = BandaiImageSearcher()
        self.image_repository = CachedImageRepository(image_cache, image_search)
        
        match format:
            case DigimonDeckFormats.DIGIMONCARDAPP:
                self.format = DigimonCardAppDeckFormat()
            case DigimonDeckFormats.DIGIMONCARDDEV:
                self.format = DigimonCardDevDeckFormat()
            case DigimonDeckFormats.DIGIMONCARDIO:
                self.format = DigimonCardIODeckFormat()
            case DigimonDeckFormats.DIGIMONMETA:
                self.format = DigimonMetaDeckFormat()
            case DigimonDeckFormats.TABLETOP_SIMULATOR:
                self.format = TTSDeckFormat()
            case DigimonDeckFormats.UNTAP:
                self.format = UntapDeckFormat()

    async def parse_deck(self, decklist):
        with open(decklist, 'r') as deck_file:
            deck_text = deck_file.read()
        return await super().parse_deck(deck_text)

    async def save_deck(self, deck):
        return await super().save_deck(deck)
