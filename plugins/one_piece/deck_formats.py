from re import compile
from enum import Enum
from typing import Callable, Tuple

card_data_tuple = Tuple[str, int, str] # card number, quantity, name

def parse_deck_helper(deck_text: str, handle_card: Callable, is_card_line: Callable[[str], bool], extract_card_data: Callable[[str], card_data_tuple]) -> None:
    error_lines = []

    index = 0
    for line in deck_text.strip().split('\n'):
        if is_card_line(line):
            index = index + 1

            card_code, quantity, name = extract_card_data(line)

            print(f'Index: {index}, quantity: {quantity}, card code: {card_code}, name: {name}')
            try:
                handle_card(index, card_code, quantity)
            except Exception as e:
                print(f'Error: {e}')
                error_lines.append((line, e))

        else:
            print(f'Skipping: "{line}"')

    if len(error_lines) > 0:
        print(f'Errors: {error_lines}')

def parse_optcgsim(deck_text: str, handle_card: Callable) -> None:
    pattern = compile(r'^(\d{1})x([A-Z0-9]+-\d+)$') # '{quantity}x{card number}'

    def is_optcgsim_line(line) -> bool:
        return bool(pattern.match(line))

    def extract_optcgsim_card_data(line) -> card_data_tuple:
        match = pattern.match(line)
        if match:
            quantity = int(match.group(1).strip())
            card_code = match.group(2).strip()

            return (card_code, quantity, '')

    parse_deck_helper(deck_text, handle_card, is_optcgsim_line, extract_optcgsim_card_data)

def parse_egman(deck_text: str, handle_card: Callable) -> None:
    pattern = compile(r'^\s*(\d+)\s+([A-Z0-9]+-\d+)\s+(.+?)\s*$') # '{quantity} {card number} {name}'

    def is_egman_line(line) -> bool:
        return bool(pattern.match(line))

    def extract_egman_card_data(line) -> card_data_tuple:
        match = pattern.match(line)
        if match:
            quantity = int(match.group(1).strip())
            card_code = match.group(2).strip()
            name = match.group(3).strip()

            return (card_code, quantity, name)

    parse_deck_helper(deck_text, handle_card, is_egman_line, extract_egman_card_data)

class DeckFormat(str, Enum):
    OPTCGSIMULATOR = 'optcgsim'
    EGMANEVENTS = 'egman'

def parse_deck(deck_text: str, format: DeckFormat, handle_card: Callable) -> None:
    if format == DeckFormat.OPTCGSIMULATOR:
        return parse_optcgsim(deck_text, handle_card)
    elif format == DeckFormat.EGMANEVENTS:
        return parse_egman(deck_text, handle_card)
    else:
        raise ValueError('Unrecognized deck format.')
