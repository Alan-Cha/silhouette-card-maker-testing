import os
import sys
import click

# Add parent directory to path to allow imports when run as a script
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, REPO_ROOT)

from plugins.yugioh.deck_formats import DeckFormat, parse_deck
from plugins.yugioh.ygoprodeck import fetch_card_art
from utilities import ensure_directory

front_directory = os.path.join(REPO_ROOT, 'game', 'front')
double_sided_directory = os.path.join(REPO_ROOT, 'game', 'double_sided')

@click.command()
@click.argument('deck_path')
@click.argument('format', type=click.Choice([t.value for t in DeckFormat], case_sensitive=False))

def cli(deck_path: str, format: DeckFormat):
    ensure_directory(front_directory)
    ensure_directory(double_sided_directory)
    if format != DeckFormat.YDKE and not os.path.isfile(deck_path):
        print(f'{deck_path} is not a valid file.')
        return

    cards = parse_deck(deck_path, format)

    for passcode, quantity in cards.items():
        fetch_card_art(passcode, quantity, front_directory)

if __name__ == '__main__':
    cli()