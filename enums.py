from enum import Enum


class CardSize(str, Enum):
    BRIDGE = "bridge"
    BRIDGE_SQUARE = "bridge_square"
    BUSINESS = "business"
    CREDIT = "credit"
    DOMINO = "domino"
    DOMINO_SQUARE = "domino_square"
    EURO_BUSINESS = "euro_business"
    EURO_MINI = "euro_mini"
    EURO_POKER = "euro_poker"
    JAPANESE = "japanese"
    JUMBO = "jumbo"
    MICRO = "micro"
    MINI = "mini"
    PHOTO = "photo"
    POKER = "poker"
    STANDARD = "standard"
    STANDARD_DOUBLE = "standard_double"
    TAROT = "tarot"


class PaperSize(str, Enum):
    LETTER = "letter"
    ANSI_A = "ansi_a"
    TABLOID = "tabloid"
    ANSI_B = "ansi_b"
    A4 = "a4"
    A3 = "a3"
    ARCH_B = "arch_b"


class Registration(str, Enum):
    THREE = "3"
    FOUR = "4"


# Paper orientation: portrait keeps cards upright, landscape rotates them 90 degrees.
class Orientation(str, Enum):
    PORTRAIT = "portrait"
    LANDSCAPE = "landscape"
