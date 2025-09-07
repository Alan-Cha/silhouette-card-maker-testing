from re import compile
from enum import Enum
from typing import Callable, Tuple
from json import loads, dumps
from swudb import fetch_name_and_title

card_data_tuple = Tuple[str, str, str, int] # Name, Title, Card Number, Quantity

def parse_deck_helper(deck_text: str, handle_card: Callable, deck_splitter: Callable, is_card_line: Callable[[str], bool], extract_card_data: Callable[[str], card_data_tuple], index: int = 0) -> int:
    error_lines = []

    deck = deck_splitter(deck_text)
    for line in deck:
        # Iterate through the swudb_json list
        if isinstance(deck, dict) and isinstance(deck.get(line), list):
            index = parse_deck_helper(dumps(deck.get(line)), handle_card, deck_splitter, is_card_line, extract_card_data, index)

        # Get item when already at bottom level of swudb_json
        elif isinstance(deck, dict) and isinstance(deck.get(line), dict) and is_card_line(deck.get(line)):
            index += 1

            name, title, card_number, quantity = extract_card_data(deck.get(line))

            print(f'Index: {index}, quantity: {quantity}, name: {name}, title: {title}, card number:{card_number}')
            try:
                handle_card(index, name, title, quantity)
            except Exception as e:
                print(f'Error: {e}')
                error_lines.append((line, e))

        elif is_card_line(line):
            index += 1

            name, title, card_number, quantity = extract_card_data(line)

            print(f'Index: {index}, quantity: {quantity}, name: {name}, title: {title}, card number:{card_number}')

            try:
                handle_card(index, name, title, quantity)
            except Exception as e:
                print(f'Error: {e}')
                error_lines.append((line, e))
        else:
            print(f'Skipping: "{line}"')

    if len(error_lines) > 0:
        print(f'Errors: {error_lines}')

    return index

def parse_swudb_json(deck_text: str, handle_card: Callable) -> None:

    def split_swudb_json_deck(deck_text: str):
        return loads(deck_text)

    def is_swudb_json_line(line) -> bool: # '{"id": "{Card Number with _ as separator}","count": {Quantity}}'
        if not isinstance(line, dict):
            return False
        return line.get('id') is not None and line.get('count') is not None

    def extract_swudb_json_card_data(line) -> card_data_tuple:
        if isinstance(line, dict):
            card_number = line.get('id').strip()
            quantity = int(line.get('count'))
            name, title = fetch_name_and_title(card_number)

            return (name, title, card_number, quantity)

    parse_deck_helper(deck_text, handle_card, split_swudb_json_deck, is_swudb_json_line, extract_swudb_json_card_data)

def parse_melee(deck_text: str, handle_card: Callable) -> None:
    pattern = compile(r'^(\d+)\s*\|\s*([\w\'\-]+(?:\s+[\w\'\-]+)*)\s*(?:\|\s*(.+))?$') # '{Quantity} {Name} | {Title}'

    def split_melee_deck(deck_text: str):
        return deck_text.strip().split('\n')

    def is_melee_line(line) -> bool:
        return bool(pattern.match(line))

    def extract_melee_card_data(line) -> card_data_tuple:
        match = pattern.match(line)
        if match:
            name = match.group(2).strip()
            title = match.group(3)
            quantity = int( match.group(1).strip() )

            return (name, '' if title is None else title.strip(), '', quantity)

    parse_deck_helper(deck_text, handle_card, split_melee_deck, is_melee_line, extract_melee_card_data)

def parse_picklist(deck_text: str, handle_card: Callable) -> None:
    pattern = compile(r'^((?:\[\s\]\s*)+)\s*([\w\'\-]+(?:\s+[\w\'\-]+)*)\s*(?:\|\s*(.+))?$') # '{Quantity as [ ]} {Name} | {Title}'

    def split_picklist_deck(deck_text: str):
        return deck_text.strip().split('\n')

    def is_picklist_line(line) -> bool:
        return bool(pattern.match(line))

    def extract_picklist_card_data(line) -> card_data_tuple:
        match = pattern.match(line)
        if match:
            name = match.group(2).strip()
            title = match.group(3)
            quantity_group = match.group(1).strip()

            return (name, '' if title is None else title.strip(), '', quantity_group.count('[ ]'))

    parse_deck_helper(deck_text, handle_card, split_picklist_deck, is_picklist_line, extract_picklist_card_data)

class DeckFormat(str, Enum):
    SWUDB_JSON = 'swudb_json'
    MELEE = 'melee'
    PICKLIST = 'picklist'

def parse_deck(deck_text: str, format: DeckFormat, handle_card: Callable) -> None:
    if format == DeckFormat.SWUDB_JSON:
        return parse_swudb_json(deck_text, handle_card)
    elif format == DeckFormat.MELEE:
        return parse_melee(deck_text, handle_card)
    elif format == DeckFormat.PICKLIST:
        return parse_picklist(deck_text, handle_card)
    else:
        raise ValueError('Unrecognized deck format.')

if __name__ == '__main__':
    parse_deck()