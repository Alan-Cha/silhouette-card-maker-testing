from re import compile
from enum import Enum
from typing import Callable, Tuple
from xml.etree import ElementTree

card_data_tuple = Tuple[str, int, str] # Name, Quantity, Serial Code

def print_card_info(index: int, quantity: int, name: str, serial_code: str) -> None:
    parts = [f'Index: {index}', f'quantity: {quantity}', f'name: {name}']
    if serial_code:
        parts.append(f'serial code: {serial_code}')
    print(', '.join(parts))

def parse_deck_helper(deck_text: str, handle_card: Callable, is_card_line: Callable[[str], bool], extract_card_data: Callable[[str], card_data_tuple]) -> None:
    error_lines = []

    index = 0
    for line in deck_text.strip().split('\n'):
        if is_card_line(line):
            index = index + 1

            name, quantity, serial_code = extract_card_data(line)

            print_card_info(index, quantity, name, serial_code)
            try:
                handle_card(index, name, serial_code, quantity)
            except Exception as e:
                print(f'Error: {e}')
                error_lines.append((line, e))

        else:
            print(f'Skipping: "{line}"')

    if len(error_lines) > 0:
        print(f'Errors: {error_lines}')

def parse_untap(deck_text: str, handle_card: Callable) -> None:
    pattern = compile(r'^(\d+)\s(.+)\s\((.+)\)$') # '{Quantity} {Name} ({Serial Code})'

    def is_untap_line(line) -> bool:
        return bool(pattern.match(line))

    def extract_untap_card_data(line) -> card_data_tuple:
        match = pattern.match(line)
        if match:
            card_name = match.group(2).strip()
            quantity = int(match.group(1).strip())
            serial_code = match.group(3).strip()

            return (card_name, quantity, serial_code)

    parse_deck_helper(deck_text, handle_card, is_untap_line, extract_untap_card_data)

def parse_octgn(deck_text: str, handle_card: Callable) -> None:
    root = ElementTree.fromstring(deck_text)
    error_lines = []

    index = 0
    for section in root.findall('section'):
        for card in section.findall('card'):
            index += 1
            quantity = int(card.get('qty', 1))
            card_name = card.text.strip() if card.text else ''
            serial_code = ''  # OCTGN format does not include serial codes

            print_card_info(index, quantity, card_name, serial_code)
            try:
                handle_card(index, card_name, serial_code, quantity)
            except Exception as e:
                print(f'Error: {e}')
                error_lines.append((card_name, e))

    if len(error_lines) > 0:
        print(f'Errors: {error_lines}')

def parse_tts(deck_text: str, handle_card: Callable) -> None:
    parse_untap(deck_text, handle_card)

class DeckFormat(str, Enum):
    UNTAP = 'untap'
    OCTGN = 'octgn'
    TABLETOP_SIMULATOR = 'tts'

def parse_deck(deck_text: str, format: DeckFormat, handle_card: Callable) -> None:
    if format == DeckFormat.UNTAP:
        return parse_untap(deck_text, handle_card)
    elif format == DeckFormat.OCTGN:
        return parse_octgn(deck_text, handle_card)
    elif format == DeckFormat.TABLETOP_SIMULATOR:
        return parse_tts(deck_text, handle_card)
    else:
        raise ValueError('Unrecognized deck format.')

if __name__ == '__main__':
    parse_deck()