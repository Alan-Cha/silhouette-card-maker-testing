from plugins.mtg.patterns import MOXFIELD_PATTERN


def test_star_symbol_in_collector_number():
    # Moxfield exports can include ★ in collector numbers for special versions
    # e.g. "1 Sol Ring (SLD) 123★"
    line = "1 Sol Ring (SLD) 123★"
    match = MOXFIELD_PATTERN.match(line)

    assert match is not None
    assert match.group(1) == "1"
    assert match.group(2) == "Sol Ring"
    assert match.group(3) == "SLD"
    assert match.group(4) == "123★"


def test_collector_number_with_dash():
    # Collector numbers like "123-456" should also be captured
    line = "1 Some Card (SET) 123-456"
    match = MOXFIELD_PATTERN.match(line)

    assert match is not None
    assert match.group(4) == "123-456"


def test_quantity_with_x():
    # Moxfield format can include "x" after quantity (e.g. "4x")
    line = "4x Lightning Bolt (2XM) 117"
    match = MOXFIELD_PATTERN.match(line)

    assert match is not None
    assert match.group(1) == "4"
    assert match.group(2) == "Lightning Bolt"
    assert match.group(3) == "2XM"
    assert match.group(4) == "117"
