#==============================================================================
# measurements.py 
#     Value + Unit string parsing and unit conversion. 
#==============================================================================

import re

MM_PER_INCH = 25.4
PT_PER_INCH = 72

_UNIT_PATTERN = re.compile(
    r"^(?P<amount>\d+(?:\.\d*)?|\.\d+)(?P<unit>[a-zA-Z%]+)?$"
)

def parse_unit_string(unit_string: str | None, valid_units: list[str]) -> tuple[float, str]:
    if unit_string is None: 
        return 0, ""
    
    match = _UNIT_PATTERN.fullmatch(unit_string.strip().lower())

    if not match:
        raise ValueError(f"Invalid unit format: {unit_string}")

    amount = match["amount"]
    unit = match["unit"] or ""

    if valid_units and (unit not in valid_units):
        raise ValueError(f"Invalid unit: {unit_string}. Valid units are {valid_units}")

    return float(amount), unit

def size_to_mm(size_string: str | None) -> float:
    valid_units = ["","in","mm"]
    amount, unit = parse_unit_string(size_string, valid_units)

    if unit == "in":
        return amount * MM_PER_INCH

    # mm or no unit
    return amount


def size_to_in(size_string: str | None) -> float:
    return size_to_mm(size_string) / MM_PER_INCH


def size_to_pt(size_string: str | None) -> float:
    return size_to_in(size_string) * PT_PER_INCH


def size_to_pixel(size_string: str | None, ppi: int) -> int:
    return round(size_to_in(size_string) * ppi)
