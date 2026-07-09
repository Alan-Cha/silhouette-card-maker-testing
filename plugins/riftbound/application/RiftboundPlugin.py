from enum import Enum

from plugins.abstraction_base.application.GamePluginAdapter import GamePlugin
from plugins.riftbound.application.PiltoverArchiveDeckFormat import PiltoverArchiveDeckFormat
from plugins.riftbound.application.PixelbornDeckFormat import PixelbornDeckFormat
from plugins.riftbound.application.TTSDeckFormat import TTSDeckFormat
from plugins.abstraction_base.infrastructure.CachedImageRepository import CachedImageRepository
from plugins.abstraction_base.infrastructure.ImageCacheAdapter import ImageCacheAdapter
from plugins.riftbound.infrastructure.RiftManaImageSearcher import RiftManaImageSearcher
from plugins.riftbound.infrastructure.PiltoverArchiveImageSearcher import PiltoverArchiveImageSearcher
from plugins.riftbound.infrastructure.RiftManaCardSearcher import RiftManaCardSeacher
from plugins.riftbound.domain.RiftboundCard import RiftboundCard
from plugins.abstraction_base.domain.Deck import Deck
from plugins.riftbound.domain.ImageServerSource import ImageServerSource

GAME_NAME = 'riftbound'

class RiftboundDeckFormats(Enum):
    PILTOVER_ARCHIVE   = 'piltover_archive'
    PIXELBORN          = 'pixelborn'
    TABLETOP_SIMULATOR = 'tts'

class RiftboundPlugin(GamePlugin):

    def __init__(self, format: RiftboundDeckFormats, image_server: ImageServerSource):
        image_cache = ImageCacheAdapter(GAME_NAME)
        match image_server:
            case ImageServerSource.RIFTMANA:
                image_search = RiftManaImageSearcher()
            case ImageServerSource.PILTOVER_ARCHIVE:
                image_search = PiltoverArchiveImageSearcher()
        self.image_repository = CachedImageRepository(image_cache, image_search)
        
        match format:
            case RiftboundDeckFormats.PILTOVER_ARCHIVE:
                self.format = PiltoverArchiveDeckFormat()
            case RiftboundDeckFormats.PIXELBORN:
                self.format = PixelbornDeckFormat()
            case RiftboundDeckFormats.TABLETOP_SIMULATOR:
                self.format = TTSDeckFormat()

    async def parse_deck(self, decklist):
        with open(decklist, 'r') as deck_file:
            deck_text = deck_file.read()
        return await super().parse_deck(deck_text)

    async def save_deck(self, deck):
        return await super().save_deck(deck)
    
    async def get_card_images_for_deck(self, deck):
        cards_of_image_deck = []

        card_searcher = RiftManaCardSeacher()

        for card in deck.cards:
            image_card: RiftboundCard = card
            if image_card.card_number is None:
                image_card.card_number = await card_searcher.get_card_number(image_card)
                image_card.id = image_card.card_number
            image_card.front_image = await self.image_repository.get_image(card)
            cards_of_image_deck.append(card)

        return Deck(cards=cards_of_image_deck)
