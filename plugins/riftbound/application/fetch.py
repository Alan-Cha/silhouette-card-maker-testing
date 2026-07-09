from sys import path
from pathlib import Path
from click import command, argument, Choice, option
from asyncio import run

# Add plugin directory to path to allow imports when run as a script
path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from plugins.riftbound.application.RiftboundPlugin import RiftboundDeckFormats, RiftboundPlugin
from plugins.riftbound.domain.ImageServerSource import ImageServerSource

@command()
@argument('deck_path')
@argument('format', type=Choice([t.value for t in RiftboundDeckFormats], case_sensitive=False))
@option("--source", default=ImageServerSource.PILTOVER_ARCHIVE.value, type=Choice([t.value for t in ImageServerSource], case_sensitive=False), show_default=True, help="The desired image source.")
def cli(deck_path: str, format: RiftboundDeckFormats, source: ImageServerSource):
    if not Path(deck_path).exists():
        print(f'{deck_path} is not a valid file.')
        return
    
    plugin = RiftboundPlugin(RiftboundDeckFormats(format), ImageServerSource(source))
    
    run(plugin.run(deck_path))

if __name__ == '__main__':
    cli()