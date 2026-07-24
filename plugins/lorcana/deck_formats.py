import re

from enum import Enum
from typing import Optional, Tuple, Callable

# Name, Variant, Quantity
card_data_tuple = Tuple[str, Optional[str], int]

# Lorcana cards are normally printed at one of five rarities: Common,
# Uncommon, Rare, Super Rare, and Legendary. Some cards additionally get a
# special alternate-art printing at one of the variant rarities below. See:
# https://lorcast.com/docs/syntax#rarity and https://lorcast.com/docs/api/cards
class CardVariant(str, Enum):
    ENCHANTED = "enchanted"
    EPIC = "epic"
    ICONIC = "iconic"
    PROMO = "promo"

# Markers that can be appended to a card's name in a decklist to request a
# special variant printing instead of the default artwork.
VARIANT_MARKERS = {
    "*E*": CardVariant.ENCHANTED,
    "*ENCHANTED*": CardVariant.ENCHANTED,
    "*EP*": CardVariant.EPIC,
    "*EPIC*": CardVariant.EPIC,
    "*I*": CardVariant.ICONIC,
    "*ICONIC*": CardVariant.ICONIC,
    "*P*": CardVariant.PROMO,
    "*PROMO*": CardVariant.PROMO,
}

def parse_deck_helper(deck_text: str, is_card_line: Callable[[str], bool], extract_card_data: Callable[[str], card_data_tuple], handle_card: Callable) -> None:
    error_lines = []

    index = 0
    for line in deck_text.strip().split('\n'):
        if is_card_line(line):
            index = index + 1

            name, variant, quantity = extract_card_data(line)

            parts = [f'Index: {index}', f'quantity: {quantity}']
            if name: parts.append(f'name: {name}')
            if variant: parts.append(f'variant: {variant.capitalize()}')
            print(', '.join(parts))
            try:
                handle_card(index, name, variant, quantity)
            except Exception as e:
                print(f'Error: {e}')
                error_lines.append((line, e))

        else:
            print(f'Skipping: "{line}"')

    if len(error_lines) > 0:
        print(f'Errors: {error_lines}')

def parse_dreamborn_list(deck_text, handle_card: Callable) -> None:
    pattern = re.compile(r'(\d+)x?\s+(.+)', re.IGNORECASE)

    def is_dreamborn_card_line(line) -> bool:
        return bool(pattern.match(line))

    def extract_dreamborn_card_data(line) -> card_data_tuple:
        match = pattern.match(line)
        quantity = int(match.group(1))
        variant = None
        name = match.group(2).strip()

        for marker, marker_variant in VARIANT_MARKERS.items():
            if marker in name:
                variant = marker_variant.value
                name = name.replace(marker, "").strip()
                break

        return (name, variant, quantity)

    parse_deck_helper(deck_text, is_dreamborn_card_line, extract_dreamborn_card_data, handle_card)

class DeckFormat(str, Enum):
    DREAMBORN = "dreamborn"

def parse_deck(deck_text: str, format: DeckFormat, handle_card: Callable) -> None:
    if format == DeckFormat.DREAMBORN:
        parse_dreamborn_list(deck_text, handle_card)
    else:
        raise ValueError("Unrecognized deck format")