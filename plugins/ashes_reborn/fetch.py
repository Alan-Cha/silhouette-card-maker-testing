import sys
from os import path
from click import command, argument, Choice, option

# Add parent directory to path to allow imports when run as a script
sys.path.insert(0, path.join(path.dirname(__file__), '..', '..'))

from plugins.ashes_reborn.deck_formats import DeckFormat, parse_deck
from plugins.ashes_reborn.ashes import get_handle_card, ImageServer

front_directory = path.join('game', 'front')

@command()
@argument('deck_path')
@argument('format', type=Choice([t.value for t in DeckFormat], case_sensitive=False))
@option("--source", default=ImageServer.ASHES.value, type=Choice([t.value for t in ImageServer], case_sensitive=False), show_default=True, help="The desired image source.")
def cli(deck_path: str, format: DeckFormat, source: ImageServer):
    if not (format == DeckFormat.ASHES_SHARE_URL or format == DeckFormat.ASHESDB_SHARE_URL) and not path.isfile(deck_path):
        print(f'{deck_path} is not a valid file.')
        return

    parse_deck(
        deck_path,
        format,
        get_handle_card(
            source,
            front_directory
        )
    )

if __name__ == '__main__':
    cli()