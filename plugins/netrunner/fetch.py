from os import path

from .deck_formats import DeckFormat, parse_deck
from .api  import get_handle_card

front_directory = path.join('game', 'front')

def fetch(deck_path: str, format: DeckFormat):
    if not path.isfile(deck_path):
        print(f'{deck_path} is not a valid file.')
        return

    with open(deck_path, 'r', encoding='utf-8') as deck_file:
        deck_text = deck_file.read()

        parse_deck(deck_text, format, get_handle_card( front_directory ))
