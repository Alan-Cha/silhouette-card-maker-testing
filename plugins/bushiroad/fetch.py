import sys
from os import path
from click import command, argument, Choice

# Add parent directory to path to allow imports when run as a script
sys.path.insert(0, path.join(path.dirname(__file__), '..', '..'))

from plugins.bushiroad.deck_formats import DeckFormat, parse_deck
from plugins.bushiroad.bushiroad import get_handle_card

front_directory = path.join('game', 'front')
back_directory = path.join('game', 'double_sided')

@command()
@argument('deck_path')
@argument('format', type=Choice([t.value for t in DeckFormat], case_sensitive=False))

def cli(deck_path: str, format: DeckFormat):
    if not (format == DeckFormat.BUSHIROAD_URL) and not path.isfile(deck_path):
        print(f'{deck_path} is not a valid file.')
        return

    parse_deck(
        deck_path,
        format,
        get_handle_card(
            front_directory,
            back_directory
        )
    )

if __name__ == '__main__':
    cli()
