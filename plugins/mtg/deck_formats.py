import csv
import io
import json
import re
from collections import OrderedDict
from enum import Enum
from typing import Any, Callable, Iterable, Tuple
from xml.etree import ElementTree as ET

import cloudscraper
import mtg_parser

from plugins.mtg.patterns import DECKSTATS_PATTERN, MOXFIELD_PATTERN
from plugins.mtg import scryfall

type DeckEntry = Tuple[CardName, SetCode | None, CollectorNumber | None, int]
type FetchCard = Callable[[CardName, SetCode | None, CollectorNumber | None], scryfall.Card]
type DeckParse = tuple[list[tuple[str, Exception]], OrderedDict[scryfall.Card, int]]

# Deck parsing needs to be overhauled w/ better abstractions.
def parse_deck_helper2(
    deck_entries: Iterable[tuple[str, DeckEntry]],
    fetch_card: FetchCard,
) -> DeckParse:
    cards = OrderedDict[scryfall.Card, int]() # annoyingly there's no shrink-wrapped ordered-default-dict.
    errors: list[tuple[str, Exception]] = []

    # `raw` sucks. this whole abstraction mechanism sucks.
    for (raw, (name, set_code, collector_number, quantity)) in deck_entries:
        parts = [f'quantity: {quantity}']
        if set_code:
            parts.append(f'set code: {set_code}')
        if collector_number:
            parts.append(f'collector number: {collector_number}')
        if name:
            parts.append(f'name: {name}')
        print('fetching: ' + ', '.join(parts))

        try:
            card = fetch_card(name, set_code, collector_number)
        except Exception as e:
            errors.append((raw, e))
            raise # DEBUG

        cards.setdefault(card, 0)
        cards[card] += quantity

    return (errors, cards)

def parse_deck_helper(
    deck_text: str,
    is_card_line: Callable[[str], bool],
    parse_deck_line: Callable[[str], DeckEntry],
    fetch_card: FetchCard,
) -> DeckParse:
    entries: list[tuple[str, DeckEntry]] = []
    for line in deck_text.strip().split('\n'):
        if is_card_line(line):
            entries.append((line, parse_deck_line(line)))
        else:
            print(f'Skipping: "{line}"')

    return parse_deck_helper2(entries, fetch_card)


# Isshin, Two Heavens as One
# Arid Mesa
# Battlefield Forge
# Blazemire Verge
# Blightstep Pathway
# Blood Crypt
def parse_simple_list(deck_text: str, fetch_card: FetchCard) ->DeckParse:
    def is_simple_card_line(line: str) -> bool:
        return bool(line.strip())

    def extract_simple_card_data(line: str) -> DeckEntry:
        return (line.strip(), None, None, 1)

    return parse_deck_helper(deck_text, is_simple_card_line, extract_simple_card_data, fetch_card)

# About
# Name Death & Taxes

# Companion
# 1 Yorion, Sky Nomad

# Deck
# 2 Arid Mesa
# 1 Lion Sash
# 1 Loran of the Third Path
# 2 Witch Enchanter


# Sideboard
# 1 Containment Priest
def parse_mtga(deck_text: str, fetch_card: FetchCard) -> DeckParse:
    pattern = re.compile(r'(\d+)x?\s+(.+?)\s+\((\w+)\)\s+(\d+)', re.IGNORECASE)
    fallback_pattern = re.compile(r'(\d+)x?\s+(.+)')

    def is_mtga_card_line(line: str) -> bool:
        return bool(pattern.match(line) or fallback_pattern.match(line))

    def extract_mtga_card_data(line: str) -> DeckEntry:
        match = pattern.match(line)
        if match:
            quantity = int(match.group(1))
            name = match.group(2).strip()
            set_code = match.group(3).strip()
            collector_number = match.group(4).strip()

            return (name, set_code, collector_number, quantity)
        else:
            # Handle simpler "1x Mountain" lines
            fallback_match = fallback_pattern.match(line)
            assert fallback_match is not None
            quantity = int(fallback_match.group(1))
            name = fallback_match.group(2).strip()

            return (name, None, None, quantity)

    return parse_deck_helper(deck_text, is_mtga_card_line, extract_mtga_card_data, fetch_card)


# 1 Abzan Battle Priest
# 1 Abzan Falconer
# 1 Aerial Surveyor
# 1 Ainok Bond-Kin
# 1 Angel of Condemnation
# 2 Witch Enchanter


# SIDEBOARD:
# 1 Containment Priest
# 3 Deafening Silence
# 2 Disruptor Flute
def parse_mtgo(deck_text: str, fetch_card: FetchCard) -> DeckParse:
    def is_mtgo_card_line(line: str) -> bool:
        line = line.strip()
        return bool(line and line[0].isdigit())

    def extract_mtgo_card_data(line: str) -> DeckEntry:
        parts = line.split(' ', 1)
        quantity = int(parts[0])
        name = parts[1].strip()
        return (name, None, None, quantity)

    return parse_deck_helper(deck_text, is_mtgo_card_line, extract_mtgo_card_data, fetch_card)


# 1x Agadeem's Awakening // Agadeem, the Undercrypt (znr) 90 [Resilience,Land]
# 1x Ancient Cornucopia (big) 16 [Maybeboard{noDeck}{noPrice},Mana Advantage]
# 1x Arachnogenesis (cmm) 647 [Maybeboard{noDeck}{noPrice},Mass Disruption]
# 1x Ashnod's Altar (ema) 218 *F* [Mana Advantage]
# 1x Assassin's Trophy (sld) 139 [Targeted Disruption]
# 2x Boseiju Reaches Skyward // Branch of Boseiju (neo) 177 [Ramp] ^Have,#37d67a^
def parse_archidekt(deck_text: str, fetch_card: FetchCard) -> DeckParse:
    pattern = re.compile(r'^(\d+)x?\s+(.+?)\s+\((\w+)\)\s+([\d\-]+).*')

    def is_archidekt_card_line(line: str) -> bool:
        return bool(pattern.match(line))

    def extract_archidekt_card_data(line: str) -> DeckEntry:
        match = pattern.match(line)
        assert match is not None
        quantity = int(match.group(1))
        name = match.group(2).strip()
        set_code = match.group(3).strip()
        collector_number = match.group(4).strip()

        return (name, set_code, collector_number, quantity)

    return parse_deck_helper(
        deck_text, is_archidekt_card_line, extract_archidekt_card_data, fetch_card
    )


# //Main
# 1 [2XM#310] Ash Barrens
# 1 Blinkmoth Nexus
# 1 Bloodstained Mire
# 1 Buried Ruin
# 2 Command Beacon

# //Sideboard
# 1 [2XM#315] Darksteel Citadel


# //Maybeboard
# 1 [MID#159] Smoldering Egg // Ashmouth Dragon
def parse_deckstats(deck_text: str, fetch_card: FetchCard) -> DeckParse:
    def is_deckstats_card_line(line: str) -> bool:
        return bool(DECKSTATS_PATTERN.match(line))

    def extract_deckstats_card_data(line: str) -> DeckEntry:
        match = DECKSTATS_PATTERN.match(line)
        assert match is not None
        quantity = int(match.group(1))
        set_code = match.group(2)
        collector_number = match.group(3)
        name = re.sub(r'\s*#!.*$', '', match.group(4).strip())

        return (name, set_code, collector_number, quantity)

    return parse_deck_helper(
        deck_text, is_deckstats_card_line, extract_deckstats_card_data, fetch_card
    )


# 1 Lulu, Loyal Hollyphant (CLB) 477 *E*
# 1 Abzan Battle Priest (IMA) 2
# 1 Abzan Falconer (ZNC) 9
# 1 Aerial Surveyor (NEC) 5
# 1 Ainok Bond-Kin (2X2) 5
# 1 Pegasus Guardian // Rescue the Foal (CLB) 36
# 4 Plains (MOM) 277
# 2 Witch Enchanter // Witch-Blessed Meadow (MH3) 239


# SIDEBOARD:
# 1 Containment Priest (M21) 13
# 1 Deafening Silence (MB2) 9
# 1 Disruptor Flute (MH3) 209
def parse_moxfield(deck_text: str, fetch_card: FetchCard) -> DeckParse:
    def is_moxfield_card_line(line: str) -> bool:
        return bool(MOXFIELD_PATTERN.match(line))

    def extract_moxfield_card_data(line: str) -> DeckEntry:
        match = MOXFIELD_PATTERN.match(line)
        assert match is not None
        quantity = int(match.group(1))
        name = match.group(2).strip()
        set_code = match.group(3).strip()
        collector_number = match.group(4).strip()

        return (name, set_code, collector_number, quantity)

    return parse_deck_helper(
        deck_text, is_moxfield_card_line, extract_moxfield_card_data, fetch_card
    )


# Scryfall deck builder JSON
def parse_scryfall_json(
    deck_text: str,
    fetch_card: FetchCard,
):
    def parse(item: dict[str, Any]) -> DeckEntry | None:
        card_digest = item.get("card_digest")
        if card_digest is None: # TODO: is this even valid? error instead?
            return None

        name = card_digest["name"] # must have `name`
        set_code = card_digest.get("set")
        collector_number = card_digest.get("collector_number")
        quantity = int(item.get("count", 1))

        return (name, set_code, collector_number, quantity)

    data = json.loads(deck_text)
    return parse_deck_helper2(
        # lazy eval to allow helper to capture exceptions
        ((json.dumps(item), deck_entry)
         for entry in data.get("entries", {}).values()
         for item in entry
         if (deck_entry := parse(item)) is not None
        ),
        fetch_card
    )


# MPCFill XML
def extract_card_name(raw_name: str) -> str:
    """Extract card name by stripping the file extension (e.g. 'Mountain.png' -> 'Mountain')."""
    parts = raw_name.split(".")
    return ".".join(parts[:-1]) if len(parts) > 1 else parts[0]


def extract_mpcfill_card_ids(deck_text: str) -> set[str]:
    """Extract all unique card IDs from MPCFill XML for prefetching."""
    data = ET.fromstring(deck_text)
    card_ids = set[str]()

    fronts = data.find("fronts")
    if fronts:
        for front in fronts.findall("card"):
            id = front.find("id").text
            assert id is not None
            card_ids.add(id)

    backs = data.find("backs")
    if backs:
        for back in backs.findall("card"):
            id = back.find("id").text
            assert id is not None
            card_ids.add(id)

    return card_ids


def parse_mpcfill_xml(deck_text: str, fetch_card: FetchCard) -> DeckParse:
    """
    Parse MPCFill XML and call fetch_card once per slot.

    Each slot represents one physical card. fetch_card signature:
        fetch_card(slot, front_id, front_name, back_id, back_name)

    back_id and back_name will be None if the slot has no custom back.
    """
    assert False, "MPCFill XML is not implemented"
    data = ET.fromstring(deck_text)
    fronts = data.find("fronts")
    backs = data.find("backs")

    card_qty = int(data.find("details").find("quantity").text)

    # Create per-slot entries: {front_id, front_name, back_id, back_name}
    slots = [
        {"front_id": None, "front_name": None, "back_id": None, "back_name": None}
        for _ in range(card_qty)
    ]

    if fronts is None:
        raise ValueError("No fronts found in decklist")

    # Assign fronts to ALL their slots
    for front in fronts.findall("card"):
        card_id = front.find("id").text
        name = extract_card_name(front.find("name").text)
        slot_indices = [int(s) for s in front.find("slots").text.split(",")]
        for slot_idx in slot_indices:
            slots[slot_idx]["front_id"] = card_id
            slots[slot_idx]["front_name"] = name

    # Assign backs to ALL their slots
    if backs:
        for back in backs.findall("card"):
            card_id = back.find("id").text
            name = extract_card_name(back.find("name").text)
            slot_indices = [int(s) for s in back.find("slots").text.split(",")]
            for slot_idx in slot_indices:
                slots[slot_idx]["back_id"] = card_id
                slots[slot_idx]["back_name"] = name

    # Call fetch_card once per slot (1-indexed for display and filenames)
    for slot_idx, slot in enumerate(slots):
        slot_num = slot_idx + 1
        if slot["front_id"] is None:
            print(f"Warning: Slot {slot_num} has no front image, skipping")
            continue

        print(f"Slot {slot_num}: {slot['front_name']}" + (f" / {slot['back_name']}" if slot['back_id'] else ""))
        handle_card(slot_num, slot["front_id"], slot["front_name"], slot["back_id"], slot["back_name"])

# CubeCobra CSV
# Exported from CubeCobra (https://cubecobra.com)
# CSV columns: name, CMC, Type, Color, Set, Collector Number, Rarity, Color Category,
#              status, Finish, maybeboard, image URL, image Back URL, tags, Notes, MTGO ID, Custom
def parse_cubecobra_csv(deck_text: str, fetch_card: FetchCard) -> DeckParse:
    reader = csv.DictReader(io.StringIO(deck_text))

    def parse(row: dict[str, Any]) -> DeckEntry:
        name = row['name']
        set_code = row['Set']
        collector_number = row['Collector Number']
        # Previous impl aggregated by `(name, set, collector-number)`.
        # Now we use the remote-caching mechanism to amortize.
        return (name, set_code, collector_number, 1)

    return parse_deck_helper2(
        # lazy eval to allow helper to capture exceptions
        ((json.dumps(row), parse(row)) for row in reader),
        fetch_card
    )

# URL Auto-Import
#   Supported sites:
#     Aetherhub, Archidekt, Deckstats, Moxfield, MTG Goldfish,
#     MTGJSON, Scryfall, Tapped Out, TCGPlayer
def parse_url(deck_url: str, fetch_card: FetchCard) -> DeckParse:
    scraper = cloudscraper.create_scraper()
    # incorrect type sig (FFS!), does indeed return `Iter[Card] | None`
    cards = mtg_parser.parse_deck(deck_url, scraper)
    if cards is None:
        print(f"Failed to parse deck from URL: {deck_url}")
        return ([(deck_url, Exception("Failed to parse deck from URL"))], OrderedDict())

    return parse_deck_helper2(
        (("", (card.name, card.extension, card.number, card.quantity))
         for card in cards),
        fetch_card
    )


class DeckFormat(str, Enum):
    ARCHIDEKT = "archidekt"
    CUBECOBRA_CSV = "cubecobra_csv"
    DECKSTATS = "deckstats"
    MOXFIELD = "moxfield"
    MPCFILL_XML = "mpcfill_xml"
    MTGA = "mtga"
    MTGO = "mtgo"
    SCRYFALL_JSON = "scryfall_json"
    SIMPLE = "simple"
    URL = "url"


def parse_deck(
    deck_text: str,
    format: DeckFormat,
    fetch_card: FetchCard,
) -> DeckParse:
    match format:
        case DeckFormat.SIMPLE:
            return parse_simple_list(deck_text, fetch_card)
        case DeckFormat.MTGA:
            return parse_mtga(deck_text, fetch_card)
        case DeckFormat.MTGO:
            return parse_mtgo(deck_text, fetch_card)
        case DeckFormat.ARCHIDEKT:
            return parse_archidekt(deck_text, fetch_card)
        case DeckFormat.DECKSTATS:
            return parse_deckstats(deck_text, fetch_card)
        case DeckFormat.MOXFIELD:
            return parse_moxfield(deck_text, fetch_card)
        case DeckFormat.SCRYFALL_JSON:
            return parse_scryfall_json(deck_text, fetch_card)
        case DeckFormat.MPCFILL_XML:
            return parse_mpcfill_xml(deck_text, fetch_card)
        case DeckFormat.CUBECOBRA_CSV:
            return parse_cubecobra_csv(deck_text, fetch_card)
        case DeckFormat.URL:
            return parse_url(deck_text, fetch_card)


def unparse(format: DeckFormat, card: 'scryfall.Card', quantity: int) -> str:
    assert 0 < quantity
    match format:
        # 1x Ancient Cornucopia (big) 16 [Maybeboard{noDeck}{noPrice},Mana Advantage]
        case DeckFormat.ARCHIDEKT: return f'{quantity}x {card.name} ({card.set}) {card.collector_number}'
        # Don't bother with all the CSV fields.
        # name, CMC, Type, Color, Set, Collector Number, Rarity, Color Category, status, Finish, maybeboard, image URL, image Back URL, tags, Notes, MTGO ID, Custom
        case DeckFormat.CUBECOBRA_CSV:
            s = io.StringIO()
            w = csv.writer(s)
            w.writerow([card.name, '', '', '', card.set, card.collector_number] + [''] * 11)
            return '\n'.join([s.getvalue()] * quantity)
        case DeckFormat.DECKSTATS: return f'{quantity} [{card.set}#{card.collector_number}] {card.name}'
        case DeckFormat.MOXFIELD: return f'{quantity} {card.name} ({card.set}) {card.collector_number}'
        case DeckFormat.MPCFILL_XML: raise NotImplemented
        case DeckFormat.MTGA: return f'{quantity}x {card.name} ({card.set}) {card.collector_number}'
        case DeckFormat.MTGO: return f'{quantity} {card.name}'
        case DeckFormat.SCRYFALL_JSON: return json.dumps({
            "count": quantity,
            "card_digest": {
                "name": card.name,
                "set": card.set,
                "collector_number": card.collector_number,
            }
        })
        case DeckFormat.SIMPLE: return '\n'.join([card.name] * quantity)
        # URL is a pseudo format and cannot be unparsed. Use moxfield syntax.
        case DeckFormat.URL: return unparse(DeckFormat.MOXFIELD, card, quantity)
