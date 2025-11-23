from re import compile
from enum import Enum
from typing import Callable, Tuple

card_data_tuple = Tuple[str, int] # Card Name, Quantity

def parse_deck_helper(deck_text: str, handle_card: Callable, is_card_line: Callable[[str], bool], extract_card_data: Callable[[str], card_data_tuple]) -> None:
    error_lines = []

    index = 0
    for line in deck_text.strip().split('\n'):
        if is_card_line(line):
            index = index + 1

            card_name, quantity = extract_card_data(line)

            print(f'Index: {index}, quantity: {quantity}, card name: {card_name}')
            try:
                handle_card(index, card_name, quantity)
            except Exception as e:
                print(f'Error: {e}')
                error_lines.append((line, e))

        else:
            print(f'Skipping: "{line}"')

    if len(error_lines) > 0:
        print(f'Errors: {error_lines}')

def parse_omnideck(deck_text: str, handle_card: Callable) -> None:
    pattern = compile(r'^(\d+)\s+(.+)$') # '{Quantity} {Name}'

    def is_omnideck_line(line) -> bool:
        return bool(pattern.match(line))
    
    def extract_omnideck_card_data(line) -> card_data_tuple:
        match = pattern.match(line)
        if match:
            card_name = match.group(2).strip()
            quantity = int( match.group(1).strip() )

            return (card_name, quantity)
        
    parse_deck_helper(deck_text, handle_card, is_omnideck_line, extract_omnideck_card_data)

class DeckFormat(str, Enum):
    OMNIDECK = "omnideck"

def parse_deck(deck_text: str, format: DeckFormat, handle_card: Callable) -> None:
    if format == DeckFormat.OMNIDECK:
        return parse_omnideck(deck_text, handle_card)
    else:
        raise ValueError("Unrecognized deck format.")
