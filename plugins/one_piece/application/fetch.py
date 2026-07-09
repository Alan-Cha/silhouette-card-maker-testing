from sys import path
from pathlib import Path
from click import command, argument, Choice
from asyncio import run

# Add plugin directory to path to allow imports when run as a script
path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from plugins.one_piece.application.OnePiecePlugin import OnePieceDeckFormats, OnePiecePlugin

@command()
@argument('deck_path')
@argument('format', type=Choice([t.value for t in OnePieceDeckFormats], case_sensitive=False))
def cli(deck_path: str, format: OnePieceDeckFormats):
    if not Path(deck_path).exists():
        print(f'{deck_path} is not a valid file.')
        return
    
    plugin = OnePiecePlugin(OnePieceDeckFormats(format))
    
    run(plugin.run(deck_path))

if __name__ == '__main__':
    cli()