import re
import enum
from typing import Callable, Iterable, TypeVar

_A = TypeVar("_A")

def partition(xs: Iterable[_A], fn: Callable[[_A], bool]) -> tuple[list[_A], list[_A]]:
    a: list[_A] = []
    b: list[_A] = []
    for x in xs:
        (a if fn(x) else b).append(x)
    return a, b

def remove_nonalphanumeric(s: str) -> str:
    return re.sub(r'[^\w]', '', s)

# Language code as printed on the card.
# n.b. Scryfall uses a different code set for their data. See `scryfall.Language`.
class MtgPrintedLanguage(enum.StrEnum):
    ENGLISH            = "en"
    SPANISH            = "sp"
    FRENCH             = "fr"
    GERMAN             = "de"
    ITALIAN            = "it"
    PORTUGUESE         = "pt"
    JAPANESE           = "jp"
    KOREAN             = "kr"
    RUSSIAN            = "ru"
    SIMPLIFIED_CHINESE = "cs"
    TRADITIONAL_CHINESE = "ct"
    ANCIENT_GREEK      = "ag"
    PHYREXIAN          = "ph"
