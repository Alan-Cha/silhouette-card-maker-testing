from __future__ import annotations

from enum import Enum

class BushiroadGameTitle(str, Enum):
    CARDFIGHT_VANGUARD = 'Cardfight Vanguard'
    WEISS_SCHWARZ      = 'Weiss Schwarz'
    SHADOWVERSE_EVOLVE = 'Shadowverse: Evolve'
    GODZILLA           = 'Godzilla'
    HOLOLIVE           = 'Hololive'

BUSHIROAD_GAME_TITLE_ID_MAPPING = {
    '1': BushiroadGameTitle.CARDFIGHT_VANGUARD,
    '2': BushiroadGameTitle.WEISS_SCHWARZ,
    '6': BushiroadGameTitle.SHADOWVERSE_EVOLVE,
    '7': BushiroadGameTitle.GODZILLA,
    '8': BushiroadGameTitle.HOLOLIVE,
}