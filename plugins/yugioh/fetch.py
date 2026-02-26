import os
import sys
import click

# Add parent directory to path to allow imports when run as a script
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from plugins.yugioh.deck_formats import DeckFormat, parse_deck
from plugins.yugioh.ygoprodeck import fetch_card_art

front_directory = os.path.join('game', 'front')
double_sided_directory = os.path.join('game', 'double_sided')

@click.command()
@click.argument('deck_path')
@click.argument('format', type=click.Choice([t.value for t in DeckFormat], case_sensitive=False))

def cli(deck_path: str, format: DeckFormat):
    if format != DeckFormat.YDKE and not os.path.isfile(deck_path):
        print(f'{deck_path} is not a valid file.')
        return

    cards = parse_deck(deck_path, format)

    for passcode, quantity in cards.items():
        fetch_card_art(passcode, quantity, front_directory)

if __name__ == '__main__':
    cli()