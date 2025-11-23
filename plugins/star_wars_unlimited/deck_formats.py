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
        if is_card_line(line):
            index += 1

            name, title, card_id, quantity = extract_card_data(line)

            print(f'Index: {index}, quantity: {quantity}, card ID: {card_id}, name: {name}, title: {title}')

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
    data = loads(deck_text)

    # Get cards from leader, base, deck, and sideboard
    cards = []
    leader = data.get("leader")
    if leader is not None:
        cards.append(leader)
    base = data.get("base")
    if base is not None:
        cards.append(base)
    cards = cards + data.get("deck", [])
    cards = cards + data.get("sideboard", [])

    for index, card in enumerate(cards, start=1):
        card_id = card.get("id")
        quantity = card.get("count", 1)
        name, title = fetch_name_and_title(card_id)

        print(f'Index: {index}, quantity: {quantity}, card ID: {card_id}, name: {name}, title: {title}')
        handle_card(index, name, title, quantity)

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
