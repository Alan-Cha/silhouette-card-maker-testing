from dataclasses import dataclass
from enum import Enum

@dataclass
class ImageServerSource(str, Enum):
    PILTOVER_ARCHIVE = 'piltover_archive'
    RIFTMANA         = 'riftmana'