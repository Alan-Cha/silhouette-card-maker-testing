from click import argument, Choice, Group

from .fetch import fetch
from .deck_formats import DeckFormat

def register_fetch(fetch_group: Group) -> None:

    @fetch_group.command(name='flesh_and_blood')
    @argument('deck_path')
    @argument('format', type=Choice([t.value for t in DeckFormat], case_sensitive=False))

    def cli(deck_path: str, format: DeckFormat):
        fetch(deck_path, format)