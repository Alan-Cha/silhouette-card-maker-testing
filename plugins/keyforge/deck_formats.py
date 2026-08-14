from enum import Enum
from typing import Callable, List, Tuple

from plugins.keyforge.archonarcana import entry_to_title, normalize_title
from plugins.keyforge.mastervault import extract_deck_id, get_deck_card_counts

card_count_tuple = Tuple[str, int] # card reference, quantity

def run_cards(cards: List[card_count_tuple], handle_card: Callable) -> None:
    error_lines = []

    index = 0
    for name, quantity in cards:
        index = index + 1

        print(f'Index: {index}, quantity: {quantity}, name: {name}')
        try:
            handle_card(index, name, quantity)
        except Exception as e:
            print(f'Error: {e}')
            error_lines.append((name, str(e)))

    if len(error_lines) > 0:
        print()
        print(f'{len(error_lines)} card(s) did not work:')
        for name, error in error_lines:
            print(f'  - {name} ({error})')

def read_lines(deck_text: str):
    for raw_line in deck_text.splitlines():
        line = raw_line.strip()

        # Skip blank lines and comments.
        if not line or line.startswith('#') or line.startswith('//'):
            continue

        yield line

def parse_archon_arcana(deck_text: str, handle_card: Callable) -> None:
    # Aggregate repeated cards into quantities, preserving first-seen order.
    ordered_keys = []
    counts = {}
    references = {}

    for line in read_lines(deck_text):
        key = normalize_title(entry_to_title(line))

        if key not in counts:
            counts[key] = 0
            ordered_keys.append(key)
            references[key] = line

        counts[key] = counts[key] + 1

    run_cards([(references[key], counts[key]) for key in ordered_keys], handle_card)

def parse_deck_url(deck_text: str, handle_card: Callable) -> None:
    cards = []
    error_lines = []

    # Each line is a deck URL. Master Vault and Decks of KeyForge share the same deck ID,
    # so both are resolved through Master Vault and can be mixed together.
    for line in read_lines(deck_text):
        try:
            deck_id = extract_deck_id(line)
            cards.extend(get_deck_card_counts(deck_id))
        except Exception as e:
            print(f'Error: {e}')
            error_lines.append((line, str(e)))

    if len(error_lines) > 0:
        print()
        print(f'{len(error_lines)} deck(s) did not work:')
        for line, error in error_lines:
            print(f'  - {line} ({error})')

    run_cards(cards, handle_card)

class DeckFormat(str, Enum):
    ARCHON_ARCANA = 'archon_arcana'
    MASTER_VAULT = 'master_vault'

def parse_deck(deck_text: str, format: DeckFormat, handle_card: Callable) -> None:
    if format == DeckFormat.ARCHON_ARCANA:
        parse_archon_arcana(deck_text, handle_card)
    elif format == DeckFormat.MASTER_VAULT:
        parse_deck_url(deck_text, handle_card)
    else:
        raise ValueError('Unrecognized deck format.')
