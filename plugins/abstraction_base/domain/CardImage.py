from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class CardImage:
    filename: str
    content_type: str
    data: bytes
