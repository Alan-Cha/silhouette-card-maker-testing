from enum import Enum
from typing import Callable, Tuple
from curiosa import get_curiosa_decklist

card_data_tuple = Tuple[str, int, str] # Name, Quantity, Image URL

def parse_deck_helper(deck_text: str, handle_card: Callable, deck_splitter: Callable, is_card_line: Callable[[str], bool], extract_card_data: Callable[[str], card_data_tuple]) -> None:
    error_lines = []

    index = 0
    for line in deck_splitter(deck_text):
        if is_card_line(line):
            index = index + 1

            name, quantity, image_url = extract_card_data(line)

            print(f'Index: {index}, quantity: {quantity}, name: {name}, image: {image_url}')
            try:
                handle_card(index, name, image_url, quantity)
            except Exception as e:
                print(f'Error: {e}')
                error_lines.append((line, e))

        else:
            print(f'Skipping: "{line}"')

    if len(error_lines) > 0:
        print(f'Errors: {error_lines}')

def parse_curiosa(deck_text: str, handle_card: Callable) -> None:

    def split_curiosa_deck(deck_text: str):
        return get_curiosa_decklist(deck_text)

    def is_curiosa_line(line) -> bool:
        if line.get('card', {}).get('name') and line.get('quantity'):
            return True
        return False

    def extract_curiosa_card_data(line) -> card_data_tuple:
        match = is_curiosa_line(line)
        if match:
            card_name = line.get('card', {}).get('name')
            quantity = line.get('quantity')
            img_variant = line.get('variantId')
            img_variants = line.get('card', {}).get('variants', [])
            card_image = next(
                (variant.get('src') for variant in img_variants if variant.get('id') == img_variant),
                img_variants[0].get('src') if img_variants else None
            )

            return (card_name, quantity, card_image)

    parse_deck_helper(deck_text, handle_card, split_curiosa_deck, is_curiosa_line, extract_curiosa_card_data)

class DeckFormat(str, Enum):
    CURIOSA = 'curiosa'

def parse_deck(deck_text: str, format: DeckFormat, handle_card: Callable) -> None:
    if format == DeckFormat.CURIOSA:
        return parse_curiosa(deck_text, handle_card)
    else:
        raise ValueError('Unrecognized deck format.')

