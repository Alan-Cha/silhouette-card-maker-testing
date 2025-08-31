from os import path
from click import command, argument, Choice, option

from deck_formats import DeckFormat, parse_deck
from ashes import get_handle_card, ImageServer

front_directory = path.join('game', 'front')

@command()
@argument('deck_path')
@argument('format', type=Choice([t.value for t in DeckFormat], case_sensitive=False))
@option("--source", default=ImageServer.ASHES.value, type=Choice([t.value for t in ImageServer], case_sensitive=False), show_default=True, help="The desired image source.")
def cli(deck_path: str, format: DeckFormat, source: ImageServer):
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