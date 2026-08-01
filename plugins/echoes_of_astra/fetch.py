import sys
from os import path
from click import command, argument, Choice

# Add parent directory to path to allow imports when run as a script
REPO_ROOT = path.abspath(path.join(path.dirname(__file__), '..', '..'))
sys.path.insert(0, REPO_ROOT)

from plugins.echoes_of_astra.deck_formats import DeckFormat, parse_deck
from plugins.echoes_of_astra.api import get_handle_card
from utilities import ensure_directory

front_directory = path.join(REPO_ROOT, 'game', 'front')

@command()
@argument('deck_path')
@argument('format', type=Choice([t.value for t in DeckFormat], case_sensitive=False))

def cli(deck_path: str, format: DeckFormat):
    ensure_directory(front_directory)
    if format != DeckFormat.ASTRA_URL and not path.isfile(deck_path):
        print(f'{deck_path} is not a valid file.')
        return

    parse_deck(deck_path, format, get_handle_card(front_directory))

if __name__ == '__main__':
    cli()
