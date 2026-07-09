from sys import path
from pathlib import Path
from click import command, argument, Choice, option
from asyncio import run

# Add plugin directory to path to allow imports when run as a script
path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from plugins.warlord.application.WarlordPlugin import WarlordDeckFormats, WarlordPlugin

@command()
@argument('deck_path')
@argument('format', type=Choice([t.value for t in WarlordDeckFormats], case_sensitive=False))
def cli(deck_path: str, format: WarlordDeckFormats):
    if not Path(deck_path).exists():
        print(f'{deck_path} is not a valid file.')
        return
    
    plugin = WarlordPlugin(WarlordDeckFormats(format))
    
    run(plugin.run(deck_path))

if __name__ == '__main__':
    cli()