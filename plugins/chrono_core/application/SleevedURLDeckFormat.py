from plugins.abstraction_base.application.DeckFormatAdapter import DeckFormat
from plugins.abstraction_base.domain.Card import Card
from plugins.abstraction_base.domain.Deck import Deck
from plugins.chrono_core.infrastructure.ChronoCoreDeckSearcher import ChronoCoreDeckSearcher

class SleevedURLDeckFormat(DeckFormat[Card]):

    def __init__(self):
        super().__init__()

    async def parse_decklist(self, decklist):
        deck_searcher = ChronoCoreDeckSearcher()

        cards_of_deck = []

        for deck_line in decklist.strip().split(self.deck_splitter_delimiter):
            is_valid_url = await deck_searcher.is_url_for_deck(deck_line)
            if is_valid_url:
                extracted_deck = await deck_searcher.extract_deck_from_url(deck_line)
                cards_of_deck += extracted_deck.cards

        return Deck(cards=cards_of_deck)