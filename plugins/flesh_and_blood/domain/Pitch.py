from dataclasses import dataclass
from enum import Enum

@dataclass
class Pitch(str, Enum):
    RED = '1'
    YELLOW = '2'
    BLUE = '3'
    NONE = ''