from typing import Protocol
from click import Group

class RegisterFetchPlugin(Protocol):
    def __call__(self, fetch_group: Group) -> None:
        """Attach one or more `fetch` subcommands to the group."""
