from enum import Enum
from _collections_abc import Set
from typing import Callable, Tuple
from re import compile
import os

from bushiroad import fetch_decklist, resolve_image_url

card_data_tuple = Tuple[str, str, str, int] # name, front_url, back_url, quantity

def parse_deck_helper(
        deck_text: str,
        handle_card: Callable,
        deck_splitter: Callable,
        is_card_line: Callable,
        extract_card_data: Callable,
    ) -> None:
    error_lines = []

    index = 0

    for line in deck_splitter(deck_text):
        if is_card_line(line):
            index = index + 1

            name, front_url, back_url, quantity = extract_card_data(line)

            parts = [f'Index: {index}', f'quantity: {quantity}']
            if name: parts.append(f'name: {name}')
            print(', '.join(parts))
            try:
                handle_card(index, name, front_url, back_url, quantity)
            except Exception as e:
                print(f'Error: {e}')
                error_lines.append((line, e))
        else:
            print(f'Skipping: "{line}"')

    if len(error_lines) > 0:
        print(f'Errors: {error_lines}')

def parse_bushiroad_url(deck_text: str, handle_card: Callable) -> None:
    DECKLOG_URL_PATTERN = compile(r'https?://decklog(?:-en)?\.bushiroad\.com/view/(\w+)\s*')

    def is_bushiroad_line(line) -> bool:
        return line.get('name') is not None and line.get('num') is not None and line.get('img') is not None

    def extract_bushiroad_card_data(line) -> card_data_tuple:
        name = line.get('name').strip()
        quantity = int(line.get('num'))
        front_url = line.get('front_url', '')
        back_url = line.get('back_url', '')
        return (name, front_url, back_url, quantity)

    def extract_deck_code(text: str) -> str:
        match = DECKLOG_URL_PATTERN.match(text)
        if match:
            return match.group(1)
        return text

    def split_bushiroad_deck(deck_text: str) -> Set[str]:
        text_iterable = deck_text.strip().split('\n')
        cards = []
        for line in text_iterable:
            line = line.strip()
            if not line:
                continue
            deck_code = extract_deck_code(line)
            game_title, deck = fetch_decklist(deck_code)
            print(f'Game: {game_title.value}')
            for card in deck:
                front_image = card.get('img', '').strip()
                card['front_url'] = resolve_image_url(game_title, front_image) if front_image else ''

                back_image = ''
                if card.get('custom_param') is not None and card.get('custom_param').get('is_bothsides'):
                    back_image = card.get('custom_param').get('rev_img', '').strip()
                card['back_url'] = resolve_image_url(game_title, back_image) if back_image else ''

                cards.append(card)
        return cards

    if os.path.isfile(deck_text):
        deck_text = open(deck_text, 'r', encoding='utf-8').read()

    parse_deck_helper(deck_text, handle_card, split_bushiroad_deck, is_bushiroad_line, extract_bushiroad_card_data)

class DeckFormat(str, Enum):
    BUSHIROAD_URL = 'bushiroad_url'

def parse_deck(deck_text: str, format: DeckFormat, handle_card: Callable) -> None:
    if format == DeckFormat.BUSHIROAD_URL:
        return parse_bushiroad_url(deck_text, handle_card)
    else:
        raise ValueError('Unrecognized deck format.')
