from enum import Enum
import os
from typing import Callable
from plugins.ashes_reborn.ashes import fetch_deck_data
from re import compile

def parse_ashes(deck_text: str, handle_card: Callable):
    SHARE_URL_PATTERN = compile(r'https\:\/\/ashes.live\/decks\/share\/(.+)\/*')
    DECK_API_URL_TEMPLATE = 'https://api.ashes.live/v2/decks/shared/{share_id}'

    if os.path.isfile(deck_text):
        deck_text = open(deck_text,"r").read()

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

        deck = fetch_deck_data(DECK_API_URL_TEMPLATE.format(share_id=match.group(1)))

        for card in deck:
            if not card.get("name") or not card.get("stub"):
                continue

            index = index + 1
            name = card.get("name")
            stub = card.get("stub")
            quantity = card.get("count") or 1

            parts = [f'Index: {index}', f'quantity: {quantity}']
            if name: parts.append(f'name: {name}')
            if stub: parts.append(f'card stub: {stub}')
            print(', '.join(parts))

            try:
                handle_card(index, name, stub, quantity)
            except Exception as e:
                print(f'Error: {e}')
                error_lines.append((name, e))

    if len(error_lines) > 0:
        print(f'Errors: {error_lines}')

def parse_ashesdb(deck_text: str, handle_card: Callable):
    SHARE_URL_PATTERN = compile(r'https\:\/\/ashesdb.plaidhatgames.com\/decks\/share\/(.+)\/*')
    DECK_API_URL_TEMPLATE = 'https://apiasheslive.plaidhatgames.com/v2/decks/shared/{share_id}'

    if os.path.isfile(deck_text):
        deck_text = open(deck_text,"r").read()

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

        deck = fetch_deck_data(DECK_API_URL_TEMPLATE.format(share_id=match.group(1)))

        for card in deck:
            if not card.get("name") or not card.get("stub"):
                continue

            index = index + 1
            name = card.get("name")
            stub = card.get("stub")
            quantity = card.get("count") or 1

            parts = [f'Index: {index}', f'quantity: {quantity}']
            if name: parts.append(f'name: {name}')
            if stub: parts.append(f'card stub: {stub}')
            print(', '.join(parts))

            try:
                handle_card(index, name, stub, quantity)
            except Exception as e:
                print(f'Error: {e}')
                error_lines.append((name, e))

    if len(error_lines) > 0:
        print(f'Errors: {error_lines}')

class DeckFormat(str, Enum):
    ASHES_SHARE_URL   = 'ashes_share_url'
    ASHESDB_SHARE_URL = 'ashesdb_share_url'

def parse_deck(deck_text: str, format: DeckFormat, handle_card: Callable):
    if format == DeckFormat.ASHES_SHARE_URL:
        parse_ashes(deck_text, handle_card)
    elif format == DeckFormat.ASHESDB_SHARE_URL:
        parse_ashesdb(deck_text, handle_card)
    else:
        raise ValueError('Unrecognized deck format.')
