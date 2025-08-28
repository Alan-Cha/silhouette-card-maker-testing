from re import compile
from enum import Enum
from typing import Callable, Tuple
from bushiroad import fetch_decklist

card_data_tuple = Tuple[str, int, str, str] # Name, Quantity, Front Image, Back Image

def parse_deck_helper(deck_text: str, handle_card: Callable, is_card_line: Callable[[str], bool], extract_card_data: Callable[[str], card_data_tuple],
                      extract_deck_data: Callable) -> None:
    error_lines = []

    index = 0
    for deck_line in deck_text.strip().split('\n'):
        game_title, deck = extract_deck_data(deck_line)
        for line in deck:
            if is_card_line(line):
                index = index + 1

                name, quantity, front_image, back_image = extract_card_data(line)

                print(f'Index: {index}, game: {game_title}, name: {name}, quantity: {quantity}, front image: {front_image}, back image: {back_image}')
                try:
                    handle_card(index, game_title, name, front_image, back_image, quantity)
                except Exception as e:
                    print(f'Error: {e}')
                    error_lines.append((line, e))

            else:
                print(f'Skipping: "{line}"')

    if len(error_lines) > 0:
        print(f'Errors: {error_lines}')

def parse_bushiroad(deck_text: str, handle_card: Callable) -> None:

    def extract_bushiroad_deck_data(line):
        return fetch_decklist(line)

    def is_bushiroad_line(line) -> bool:
        return line.get('name') is not None and line.get('num') is not None and line.get('img') is not None

    def extract_bushiroad_card_data(line) -> card_data_tuple:
        back_image = ''
        if line.get('custom_param') is not None and line.get('custom_param').get('is_bothsides'): # Shadowverse: Evolve
            back_image = line.get('custom_param').get('rev_img').strip()
        return (line.get('name').strip(), int(line.get('num')), line.get('img').strip(), back_image)

    parse_deck_helper(deck_text, handle_card, is_bushiroad_line, extract_bushiroad_card_data, extract_bushiroad_deck_data)

class DeckFormat(str, Enum):
    BUSHIROAD = 'bushiroad'

def parse_deck(deck_text: str, format: DeckFormat, handle_card: Callable) -> None:
    if format == DeckFormat.BUSHIROAD:
        return parse_bushiroad(deck_text, handle_card)
    else:
        raise ValueError('Unrecognized deck format.')

if __name__ == '__main__':
    parse_deck()