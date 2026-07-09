from sys import path
from pathlib import Path
from click import command, argument, Choice, option
from asyncio import run

# Add plugin directory to path to allow imports when run as a script
path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from plugins.ashes_reborn.application.AshesRebornPlugin import AshesRebornDeckFormats, AshesRebornPlugin, URL_DECK_FORMATS
from plugins.ashes_reborn.domain.ImageServerSource import ImageServerSource

@command()
@argument('deck_path')
@argument('format', type=Choice([t.value for t in AshesRebornDeckFormats], case_sensitive=False))
@option("--source", default=ImageServerSource.ASHES.value, type=Choice([t.value for t in ImageServerSource], case_sensitive=False), show_default=True, help="The desired image source.")
def cli(deck_path: str, format: AshesRebornDeckFormats, source: ImageServerSource):
    is_deck_a_file: bool = Path(deck_path).exists()

    if not AshesRebornDeckFormats(format) in URL_DECK_FORMATS and not is_deck_a_file:
        print(f'{deck_path} is not a valid file.')
        return
    
    plugin = AshesRebornPlugin(AshesRebornDeckFormats(format), ImageServerSource(source))
    
    run(plugin.run(deck_path))

if __name__ == '__main__':
    cli()