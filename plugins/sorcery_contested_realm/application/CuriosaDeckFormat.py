from plugins.abstraction_base.application.DeckFormatAdapter import DeckFormat
from plugins.sorcery_contested_realm.domain.SorceryCard import SorceryCard
from plugins.abstraction_base.domain.Deck import Deck
from plugins.sorcery_contested_realm.infrastructure.CuriosaDeckSearcher import CuriosaDeckSearcher

class CuriosaDeckFormat(DeckFormat[SorceryCard]):

    def __init__(self):
        super().__init__()

    async def is_card_line_of_format(self, card_line):
        return card_line.get('card', {}).get('name') and card_line.get('quantity')

    async def extract_card_data_from_card_line(self, card_line, index):
        match = await self.is_card_line_of_format(card_line)
        if match:
            quantity = card_line.get('quantity')
            name = card_line.get('card', {}).get('name')

            img_variant = card_line.get('variantId')
            img_variants = card_line.get('card', {}).get('variants', [])
            card_image_url = next(
                (variant.get('src') for variant in img_variants if variant.get('id') == img_variant),
                img_variants[0].get('src') if img_variants else None
            )

            return SorceryCard(
                id = name,
                name = name,
                quantity = quantity,
                placements = [index for _ in range(quantity)],
                front_image = None,
                back_image = None,
                variant_image_url = card_image_url
            )
    
    async def parse_decklist(self, decklist):
        deck_searcher = CuriosaDeckSearcher()

        cards_of_deck: list[SorceryCard] = []

        for deck_line in decklist.strip().split(self.deck_splitter_delimiter):
            is_valid_url = await deck_searcher.is_url_for_deck(deck_line)
            if is_valid_url:
                extracted_deck = await deck_searcher.extract_deck_from_url(deck_line)
                cards_of_deck += extracted_deck.cards

        return Deck(cards=cards_of_deck)