from click import argument, option, Choice, Group

from .fetch import fetch
from .deck_formats import DeckFormat
from .api import ImageServer

def register_fetch(fetch_group: Group) -> None:

    @fetch_group.command(name='riftbound')
    @argument('deck_path')
    @argument('format', type=Choice([t.value for t in DeckFormat], case_sensitive=False))
    @option("--source", default=ImageServer.PILTOVER.value, type=Choice([t.value for t in ImageServer], case_sensitive=False), show_default=True, help="The desired image source.")

    def cli(deck_path: str, format: DeckFormat):
        fetch(deck_path, format)