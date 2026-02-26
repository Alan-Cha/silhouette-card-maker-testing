import sys
from os import path
from click import command, argument, Choice

# Add parent directory to path to allow imports when run as a script
sys.path.insert(0, path.join(path.dirname(__file__), '..', '..'))

from plugins.gundam.deck_formats import DeckFormat, parse_deck
from plugins.gundam.gundam import get_handle_card

front_directory = path.join('game', 'front')
double_sided_directory = path.join('game', 'double_sided')

@command()
@argument('deck_path')
@argument('format', type=Choice([t.value for t in DeckFormat], case_sensitive=False))

def cli(deck_path: str, format: DeckFormat):
    if not path.isfile(deck_path):
        print(f'{deck_path} is not a valid file.')
        return

    with open(deck_path, 'r') as deck_file:
        deck_text = deck_file.read()

        parse_deck(deck_text, format, get_handle_card(front_directory))

if __name__ == '__main__':
    cli()