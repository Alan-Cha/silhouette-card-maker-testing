from re import compile
from enum import Enum
from typing import Callable, Tuple

card_data_tuple = Tuple[str, int, str, int] # Name, Quantity, Set ID, Card Number

def parse_deck_helper(deck_text: str, handle_card: Callable, is_card_line: Callable[[str], bool], extract_card_data: Callable[[str], card_data_tuple]) -> None:
    error_lines = []

    index = 0
    for line in deck_text.strip().split('\n'):
        if is_card_line(line):
            index = index + 1

            name, quantity, set_id, card_no = extract_card_data(line)

            parts = [f'Index: {index}', f'quantity: {quantity}']
            if name: parts.append(f'name: {name}')
            if set_id: parts.append(f'set: {set_id}')
            if card_no: parts.append(f'card number: {card_no}')
            print(', '.join(parts))
            try:
                handle_card(index, name, set_id, card_no, quantity)
            except Exception as e:
                print(f'Error: {e}')
                error_lines.append((line, e))

        else:
            print(f'Skipping: "{line}"')

    if len(error_lines) > 0:
        print(f'Errors: {error_lines}')

def parse_limitless(deck_text: str, handle_card: Callable) -> None:
    pattern = compile(r'^(\d+)\s(.+)\s(.+)\s(\d+)$') # '{Quantity} {Name} {Set} {Number}'

    def is_limitless_line(line) -> bool:
        return bool(pattern.match(line))

    def extract_limitless_card_data(line) -> card_data_tuple:
        match = pattern.match(line)
        if match:
            card_name = match.group(2).strip()
            quantity = int(match.group(1).strip())
            set_id = match.group(3).strip()
            card_number = int(match.group(4).strip())

            return (card_name, quantity, set_id, card_number)

    parse_deck_helper(deck_text, handle_card, is_limitless_line, extract_limitless_card_data)

class DeckFormat(str, Enum):
    LIMITLESS = 'limitless'

def parse_deck(deck_text: str, format: DeckFormat, handle_card: Callable) -> None:
    if format == DeckFormat.LIMITLESS:
        return parse_limitless(deck_text, handle_card)
    else:
        raise ValueError('Unrecognized deck format.')

