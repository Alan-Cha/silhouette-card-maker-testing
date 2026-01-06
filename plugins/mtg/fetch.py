import os

from .deck_formats import DeckFormat, parse_deck
from .scryfall import get_handle_card as scryfall_get_handle_card
from .mpcfill import get_handle_card as mpc_get_handle_card

from typing import Set

front_directory = os.path.join('game', 'front')
double_sided_directory = os.path.join('game', 'double_sided')

def fetch(
    deck_path: str,
    format: DeckFormat,
    ignore_set_and_collector_number: bool,

    prefer_older_sets: bool,
    prefer_set: Set[str],

    prefer_showcase: bool,
    prefer_extra_art: bool,
    tokens: bool
):
    if not os.path.isfile(deck_path):
        print(f'{deck_path} is not a valid file.')
        return
    
    if format == DeckFormat.MPCFILL_XML:
        get_handle_card = mpc_get_handle_card(
            front_directory,
            double_sided_directory
        )
    else:
        get_handle_card = scryfall_get_handle_card(
            ignore_set_and_collector_number,

            prefer_older_sets,
            prefer_set,
            
            prefer_showcase,
            prefer_extra_art,
            tokens,

            front_directory,
            double_sided_directory
        )

    with open(deck_path, 'r') as deck_file:
        deck_text = deck_file.read()

        parse_deck(
            deck_text,
            format,
            get_handle_card,
        )
