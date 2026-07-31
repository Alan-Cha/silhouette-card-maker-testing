import json
import os
from enum import Enum
from re import compile
from typing import Callable

from plugins.arkham_horror_lcg.api import fetch_arkhamdb_deck

DECK_URL_PATTERN = compile(r'https?://arkhamdb\.com/(deck|decklist)/view/(\d+)')

def handle_slots(data: dict, handle_card: Callable) -> None:
    error_lines = []
    index = 0

    slots = dict(data.get('slots', {}))

    investigator_code = data.get('investigator_code')
    if investigator_code:
        slots[investigator_code] = slots.get(investigator_code, 0) + 1

    for code, quantity in slots.items():
        index += 1

        print(f'Index: {index}, quantity: {quantity}, code: {code}')
        try:
            handle_card(index, code, quantity)
        except Exception as e:
            print(f'Error: {e}')
            error_lines.append((code, e))

    if len(error_lines) > 0:
        print(f'Errors: {error_lines}')

# ArkhamDB deck export JSON
# {
#   "investigator_code": "01001",
#   "slots": {
#     "01006": 1,
#     "01016": 1,
#     "01086": 2
#   }
# }
def parse_arkhamdb_json(deck_text: str, handle_card: Callable) -> None:
    data = json.loads(deck_text)
    handle_slots(data, handle_card)

# ArkhamDB URL format
#   https://arkhamdb.com/deck/view/12345
#   https://arkhamdb.com/decklist/view/12345
def parse_arkhamdb_url(deck_text: str, handle_card: Callable) -> None:
    if os.path.isfile(deck_text):
        with open(deck_text, 'r') as deck_file:
            deck_text = deck_file.read()

    deck_text = deck_text.strip()

    match = DECK_URL_PATTERN.match(deck_text)
    if not match:
        print(f'"{deck_text}" is not a valid ArkhamDB deck URL.')
        return

    is_decklist = match.group(1) == 'decklist'
    deck_id = match.group(2)

    data = fetch_arkhamdb_deck(deck_id, is_decklist)
    handle_slots(data, handle_card)

class DeckFormat(str, Enum):
    ARKHAMDB_JSON = 'arkhamdb_json'
    ARKHAMDB_URL = 'arkhamdb_url'

def parse_deck(deck_text: str, format: DeckFormat, handle_card: Callable) -> None:
    if format == DeckFormat.ARKHAMDB_JSON:
        parse_arkhamdb_json(deck_text, handle_card)
    elif format == DeckFormat.ARKHAMDB_URL:
        parse_arkhamdb_url(deck_text, handle_card)
    else:
        raise ValueError('Unrecognized deck format.')
