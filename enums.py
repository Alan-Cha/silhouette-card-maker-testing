from enum import Enum


class CardSize(str, Enum):
    STANDARD = "standard"
    STANDARD_DOUBLE = "standard_double"
    JAPANESE = "japanese"
    POKER = "poker"
    POKER_HALF = "poker_half"
    BRIDGE = "bridge"
    BRIDGE_SQUARE = "bridge_square"
    TAROT = "tarot"
    DOMINO = "domino"
    DOMINO_SQUARE = "domino_square"


class PaperSize(str, Enum):
    LETTER = "letter"
    TABLOID = "tabloid"
    A4 = "a4"
    A3 = "a3"
    ARCHB = "archb"


class Registration(str, Enum):
    THREE = "3"
    FOUR = "4"


class Orientation(str, Enum):
    VERTICAL = "vertical"
    HORIZONTAL = "horizontal"
