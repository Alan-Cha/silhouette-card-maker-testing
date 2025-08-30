from enum import Enum
from _collections_abc import Set
from typing import Callable, Tuple
from ashes import fetch_deck_data
from re import compile

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

            name, stub, quantity = extract_card_data(line)

            print(f'Index: {index}, quantity: {quantity}, stub: {stub}, name: {name}')
            try:
                handle_card(index, name, stub, quantity)
            except Exception as e:
                print(f'Error: {e}')
                error_lines.append((line, e))
        else:
            print(f'Skipping: "{line}"')

    if len(error_lines) > 0:
        print(f'Errors: {error_lines}')

def parse_ashes(deck_text: str, handle_card: Callable):
    SHARE_DECK_PATTERN = compile(r'https\:\/\/ashes.live\/decks\/share\/(.+)\/*')

    def is_ashes_deck(deck_url: str) -> bool:
        return bool(SHARE_DECK_PATTERN.match(deck_url))

    def is_ashes_line(line) -> bool:
        return line.get("name") and line.get("stub")

    def extract_ashes_card_data(line) -> card_data_tuple:
        if is_ashes_line(line):
            quantity = line.get("count") or 1
            name = line.get("name")
            stub = line.get("stub")

            return (name, stub, quantity)

    def split_ashes_deck(deck_text: str) -> Set[str]:
        text_iterable = deck_text.strip().split('\n')
        decks = []
        for text in text_iterable:
            if is_ashes_deck(text):
                match = SHARE_DECK_PATTERN.match(text)
                deck = fetch_deck_data(match.group(1))
                decks += deck
        return deck

    parse_deck_helper(deck_text, handle_card, split_ashes_deck, is_ashes_line, extract_ashes_card_data)

class DeckFormat(str, Enum):
    ASHES = 'ashes'

def parse_deck(deck_text: str, format: DeckFormat, handle_card: Callable):
    if format == DeckFormat.ASHES:
        parse_ashes(deck_text, handle_card)
    else:
        raise ValueError('Unrecognized deck format.')

if __name__ == '__main__':
    parse_deck()