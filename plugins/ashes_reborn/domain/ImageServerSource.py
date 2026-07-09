from dataclasses import dataclass
from enum import Enum

@dataclass
class ImageServerSource(str, Enum):
    ASHES   = 'ashes'
    ASHESDB = 'ashesdb'