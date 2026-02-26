import sys
from os import path
from click import command, argument, Choice

# Add parent directory to path to allow imports when run as a script
sys.path.insert(0, path.join(path.dirname(__file__), '..', '..'))

from plugins.elestrals.deck_formats import DeckFormat, parse_deck
from plugins.elestrals.elestrals import get_handle_card

front_directory = path.join('game', 'front')

@command()
@argument('deck_path')
@argument('format', type=Choice([t.value for t in DeckFormat], case_sensitive=False))

def cli(deck_path: str, format: DeckFormat):
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

if __name__ == '__main__':
    cli()