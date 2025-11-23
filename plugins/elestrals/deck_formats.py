from enum import Enum
from _collections_abc import Set
from typing import Callable, Tuple
from elestrals import fetch_deck_data

card_data_tuple = Tuple[str, str, int] # name, image, quantity

def parse_deck_helper(
        deck_text: str,
        handle_card: Callable,
        deck_splitter: Callable,
        is_card_line: Callable,
        extract_card_data: Callable,
    ) -> None:
    error_lines = []

    index = 0

    for line in deck_splitter(deck_text):
        if is_card_line(line):
            index = index + 1

            name, image, quantity = extract_card_data(line)

            print(f'Index: {index}, quantity: {quantity}, image: {image}, name: {name}')
            try:
                handle_card(index, name, image, quantity)
            except Exception as e:
                print(f'Error: {e}')
                error_lines.append((line, e))
        else:
            print(f'Skipping: "{line}"')

    if len(error_lines) > 0:
        print(f'Errors: {error_lines}')

def parse_elestrals(deck_text: str, handle_card: Callable):
    CARD_INFORMATION = {}

    def is_elestrals_line(line) -> bool:
        return line.get("cardId") and line.get("count")

    def extract_elestrals_card_data(line) -> card_data_tuple:
        if is_elestrals_line(line):
            quantity = line.get("count")
            card = CARD_INFORMATION.get(line.get("cardId"))
            name = card.get("Name")
            image = card.get("Image")

            return (name, image, quantity)

    def split_elestrals_deck(deck_text: str) -> Set[str]:
        text_iterable = deck_text.strip().split('\n')
        decks = []
        for text in text_iterable:
            deck, cards = fetch_deck_data(text)
            decks += deck
            CARD_INFORMATION.update(cards)
        return deck

    parse_deck_helper(deck_text, handle_card, split_elestrals_deck, is_elestrals_line, extract_elestrals_card_data)

class DeckFormat(str, Enum):
    ELESTRALS_PLAY_NETWORK = 'elestrals'

def parse_deck(deck_text: str, format: DeckFormat, handle_card: Callable):
    if format == DeckFormat.ELESTRALS_PLAY_NETWORK:
        parse_elestrals(deck_text, handle_card)
    else:
        raise ValueError('Unrecognized deck format.')
