from os import path

from .deck_formats import DeckFormat, parse_deck
from .gatcg  import get_handle_card

front_directory = path.join('game', 'front')
double_sided_directory = path.join('game', 'double_sided')

def fetch(deck_path: str, format: DeckFormat):
    if not path.isfile(deck_path):
        print(f'{deck_path} is not a valid file.')
        return

    with open(deck_path, 'r') as deck_file:
        deck_text = deck_file.read()

        parse_deck(deck_text, format, get_handle_card( front_directory ))
