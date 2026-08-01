import sys
from os import path
from click import command, argument, option, Choice

# Add parent directory to path to allow imports when run as a script
REPO_ROOT = path.abspath(path.join(path.dirname(__file__), '..', '..'))
sys.path.insert(0, REPO_ROOT)

from plugins.riftbound.deck_formats import DeckFormat, parse_deck
from plugins.riftbound.api import fetch_card_art, ImageServer, get_handle_card
from utilities import ensure_directory

front_directory = path.join(REPO_ROOT, 'game', 'front')
double_sided_directory = path.join(REPO_ROOT, 'game', 'double_sided')

@command()
@argument('deck_path')
@argument('format', type=Choice([t.value for t in DeckFormat], case_sensitive=False))
@option("--source", default=ImageServer.PILTOVER.value, type=Choice([t.value for t in ImageServer], case_sensitive=False), show_default=True, help="The desired image source.")

def cli(deck_path: str, format: DeckFormat, source: ImageServer):
    ensure_directory(front_directory)
    ensure_directory(double_sided_directory)
    if not path.isfile(deck_path):
        print(f'{deck_path} is not a valid file.')
        return

    with open(deck_path, 'r') as deck_file:
        deck_text = deck_file.read()

        parse_deck(
            deck_text,
            format,
            get_handle_card(
                source,
                front_directory
            )
        )

if __name__ == '__main__':
    cli()