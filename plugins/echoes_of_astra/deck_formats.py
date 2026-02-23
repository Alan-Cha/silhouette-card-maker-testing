from enum import Enum
from typing import Callable
from re import compile
import os
from plugins.echoes_of_astra.api import get_astra_deck

def parse_astra(deck_text: str, handle_card: Callable) -> None:
    SHARE_URL_PATTERN = compile(r'https\:\/\/www\.astra-builder\.com\/\w+\/create\?deck=(\d+)')

    if os.path.isfile(deck_text):
        deck_text = open(deck_text, "r").read()

    error_lines = []
    index = 0

    for line in deck_text.strip().split('\n'):
        line = line.strip()
        if not line:
            continue

        match = SHARE_URL_PATTERN.match(line)
        if not match:
            print(f'Skipping: "{line}"')
            continue

        deck = get_astra_deck(match.group(1))

        for card in deck:
            if not card.get('quantity') or not card.get('cards', {}).get('name') or not card.get('cards', {}).get('image_url'):
                continue

            index = index + 1
            name = card.get('cards').get('name')
            quantity = card.get('quantity')
            image_url = card.get('cards').get('image_url')

            parts = [f'Index: {index}', f'quantity: {quantity}']
            if name: parts.append(f'name: {name}')
            if image_url: parts.append(f'image url: {image_url}')
            print(', '.join(parts))

            try:
                handle_card(index, name, image_url, quantity)
            except Exception as e:
                print(f'Error: {e}')
                error_lines.append((name, e))

    if len(error_lines) > 0:
        print(f'Errors: {error_lines}')

class DeckFormat(str, Enum):
    ASTRA_URL = 'astrabuilder_url'

def parse_deck(deck_text: str, format: DeckFormat, handle_card: Callable) -> None:
    if format == DeckFormat.ASTRA_URL:
        return parse_astra(deck_text, handle_card)
    else:
        raise ValueError('Unrecognized deck format.')
