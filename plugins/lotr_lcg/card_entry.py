from dataclasses import dataclass


@dataclass
class CardEntry:
    """
    Represents a card entry from a decklist, fellowship, or scenario.

    Used throughout the LOTR LCG plugin to pass card information between
    parsing and fetching functions.
    """
    card_code: str
    name: str
    image_url: str
    quantity: int
    back_image_url: str | None = None
