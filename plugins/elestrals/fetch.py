from os import path

from .deck_formats import DeckFormat, parse_deck
from .elestrals import get_handle_card

front_directory = path.join('game', 'front')

def fetch(deck_path: str, format: DeckFormat):
    # if format != DeckFormat.ELESTRALS and not path.isfile(deck_path):
    #     print(f'{deck_path} is not a valid file.')
    #     return

    parse_deck(
        deck_path,
        format,
        get_handle_card(
            front_directory
        )
    )
