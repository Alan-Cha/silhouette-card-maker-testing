from enum import Enum
from typing import Callable, Tuple
from api import get_astra_deck

card_data_tuple = Tuple[str, int, str] # Name, Quantity, Image

def parse_deck_helper(deck_text: str, handle_card: Callable, deck_splitter: Callable, is_card_line: Callable[[str], bool], extract_card_data: Callable[[str], card_data_tuple]) -> None:
    error_lines = []

    index = 0
    for line in deck_splitter(deck_text):
        if is_card_line(line):
            index = index + 1

            name, quantity, image_url = extract_card_data(line)

            print(f'Index: {index}, quantity: {quantity}, name: {name}, image url: {image_url}')
            try:
                handle_card(index, name, image_url, quantity)
            except Exception as e:
                print(f'Error: {e}')
                error_lines.append((line, e))

        else:
            print(f'Skipping: "{line}"')

    if len(error_lines) > 0:
        print(f'Errors: {error_lines}')

def parse_astra(deck_text: str, handle_card: Callable) -> None:

    def is_astra_line(line) -> bool:
        return bool(line.get('quantity') and line.get('cards', {}).get('name') and line.get('cards', {}).get('image_url'))

    def extract_astra_card_data(line) -> card_data_tuple:
        match = is_astra_line(line)
        if match:
            quantity = line.get('quantity')
            card_name = line.get('cards').get('name')
            image_url = line.get('cards').get('image_url')

            return (card_name, quantity, image_url)

    parse_deck_helper(deck_text, handle_card, get_astra_deck, is_astra_line, extract_astra_card_data)

class DeckFormat(str, Enum):
    ASTRA = 'astrabuilder'

def parse_deck(deck_text: str, format: DeckFormat, handle_card: Callable) -> None:
    if format == DeckFormat.ASTRA:
        return parse_astra(deck_text, handle_card)
    else:
        raise ValueError('Unrecognized deck format.')

if __name__ == '__main__':
    parse_deck()
