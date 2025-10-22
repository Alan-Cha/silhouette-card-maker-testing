import json
import re

from enum import Enum
from typing import Callable, Tuple
from xml.etree import ElementTree as ET

from scryfall import remove_nonalphanumeric

card_data_tuple = Tuple[str, str, int, int]

def parse_deck_helper(deck_text: str, is_card_line: Callable[[str], bool], extract_card_data: Callable[[str], card_data_tuple], handle_card: Callable) -> None:
    error_lines = []

    index = 0
    for line in deck_text.strip().split('\n'):
        if is_card_line(line):
            index = index + 1

            name, set_code, collector_number, quantity = extract_card_data(line)

            print(f'Index: {index}, quantity: {quantity}, set code: {set_code}, collector number: {collector_number}, name: {name}')
            try:
                handle_card(index, name, set_code, collector_number, quantity)
            except Exception as e:
                print(f'Error: {e}')
                error_lines.append((line, e))

        else:
            print(f'Skipping: "{line}"')

    if len(error_lines) > 0:
        print(f'Errors: {error_lines}')

# Isshin, Two Heavens as One
# Arid Mesa
# Battlefield Forge
# Blazemire Verge
# Blightstep Pathway
# Blood Crypt
def parse_simple_list(deck_text, handle_card: Callable) -> None:
    def is_simple_card_line(line) -> bool:
        return bool(line.strip())

    def extract_simple_card_data(line) -> card_data_tuple:
        return (line.strip(), "", "", 1)

    parse_deck_helper(deck_text, is_simple_card_line, extract_simple_card_data, handle_card)

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
def parse_mtga(deck_text, handle_card: Callable) -> None:
    pattern = re.compile(r'(\d+)x?\s+(.+?)\s+\((\w+)\)\s+(\d+)', re.IGNORECASE)
    fallback_pattern = re.compile(r'(\d+)x?\s+(.+)')

    def is_mtga_card_line(line) -> bool:
        return bool(pattern.match(line) or fallback_pattern.match(line))

    def extract_mtga_card_data(line) -> card_data_tuple:
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
            quantity = int(fallback_match.group(1))
            name = fallback_match.group(2).strip()

            return (name, "", "", quantity)

    parse_deck_helper(deck_text, is_mtga_card_line, extract_mtga_card_data, handle_card)

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
def parse_mtgo(deck_text, handle_card: Callable) -> None:
    def is_mtgo_card_line(line) -> bool:
        line = line.strip()
        return bool(line and line[0].isdigit())

    def extract_mtgo_card_data(line) -> card_data_tuple:
        parts = line.split(' ', 1)
        quantity = int(parts[0])
        name = parts[1].strip()
        return (name, "", "", quantity)

    parse_deck_helper(deck_text, is_mtgo_card_line, extract_mtgo_card_data, handle_card)

# 1x Agadeem's Awakening // Agadeem, the Undercrypt (znr) 90 [Resilience,Land]
# 1x Ancient Cornucopia (big) 16 [Maybeboard{noDeck}{noPrice},Mana Advantage]
# 1x Arachnogenesis (cmm) 647 [Maybeboard{noDeck}{noPrice},Mass Disruption]
# 1x Ashnod's Altar (ema) 218 *F* [Mana Advantage]
# 1x Assassin's Trophy (sld) 139 [Targeted Disruption]
# 2x Boseiju Reaches Skyward // Branch of Boseiju (neo) 177 [Ramp] ^Have,#37d67a^
def parse_archidekt(deck_text, handle_card: Callable) -> None:
    pattern = re.compile(r'^(\d+)x?\s+(.+?)\s+\((\w+)\)\s+([\w\-]+).*')
    def is_archidekt_card_line(line: str) -> bool:
        return bool(pattern.match(line))

    def extract_archidekt_card_data(line: str) -> card_data_tuple:
        match = pattern.match(line)
        quantity = int(match.group(1))
        name = match.group(2).strip()
        set_code = match.group(3).strip()
        collector_number = match.group(4).strip()

        return (name, set_code, collector_number, quantity)

    parse_deck_helper(deck_text, is_archidekt_card_line, extract_archidekt_card_data, handle_card)

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
def parse_deckstats(deck_text, handle_card: Callable) -> None:
    pattern = re.compile(r'^(\d+)\s+(?:\[(\w+)?#(\w+)\]\s+)?(.+)$')
    def is_deckstats_card_line(line: str) -> bool:
        return bool(pattern.match(line))

    def extract_deckstats_card_data(line: str) -> card_data_tuple:
        match = pattern.match(line)
        quantity = int(match.group(1))
        set_code = match.group(2) or ""
        collector_number = match.group(3) or ""
        name = match.group(4).strip()

        return (name, set_code, collector_number, quantity)

    parse_deck_helper(deck_text, is_deckstats_card_line, extract_deckstats_card_data, handle_card)

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
def parse_moxfield(deck_text, handle_card: Callable) -> None:
    pattern = re.compile(r'^(\d+)\s+(.+?)\s+\((\w+)\)\s+([\w\-]+)')
    def is_moxfield_card_line(line: str) -> bool:
        return bool(pattern.match(line))

    def extract_moxfield_card_data(line: str) -> card_data_tuple:
        match = pattern.match(line)
        quantity = int(match.group(1))
        name = match.group(2).strip()
        set_code = match.group(3).strip()
        collector_number = match.group(4).strip()

        return (name, set_code, collector_number, quantity)

    parse_deck_helper(deck_text, is_moxfield_card_line, extract_moxfield_card_data, handle_card)

# Scryfall deck builder JSON
def parse_scryfall_json(deck_text, handle_card: Callable) -> None:
    data = json.loads(deck_text)
    entries = data.get("entries", {})
    items = entries.get("mainboard", []) + entries.get("sideboard", []) + entries.get("maybeboard", [])

    for index, item in enumerate(items, start=1):
        card_digest = item.get("card_digest", {})
        if card_digest is None:
            continue

        name = card_digest.get("name", "")
        set_code = card_digest.get("set", "")
        collector_number = card_digest.get("collector_number", "")
        quantity = item.get("count", 1)

        print(f'Index: {index}, quantity: {quantity}, set code: {set_code}, collector number: {collector_number}, name: {name}')
        handle_card(index, name, set_code, collector_number, quantity)

# MPCFill XML parser
def parse_mpcfill(deck_text, handle_card: Callable) -> None:
    # We need to convert this into a more usable format for sanity
    # The back field will only exist if the back of a card exists
    # {
    #     "id": "card_id",
    #     "name": "clean_card_name",
    #     "quantity": "quantity"
    #     "back": "back_card_id"
    # }
    data = ET.fromstring(deck_text)
    fronts = data.find("fronts")
    backs = data.find("backs")

    card_qty = int(data.find("details").find("quantity").text)

    decklist = [None] * card_qty
    if fronts is None:
        raise ValueError("No fronts found in decklist")
    for front in fronts.findall("card"):
        card_id = front.find("id").text
        clean_card_name = remove_nonalphanumeric(".".join(front.find("name").text.split(".")[:-1]))
        slots = front.find("slots").text.split(",")
        quantity = len(slots)
        print(clean_card_name, quantity)
        decklist[int(slots[0])] = {"id": card_id, "name": clean_card_name, "quantity": quantity}
    if backs:
        for back in backs.findall("card"):
            card_id = back.find("id").text
            slots = back.find("slots").text.split(",")
            decklist[int(slots[0])]["back"] = card_id

    decklist = [x for x in decklist if x]

    for index, item in enumerate(decklist, start=1):
        print(f"Index: {index}, Quantity: {item['quantity']}, name: {item['name']}")
        handle_card(index, item["id"], item["name"], item.get("back", None), item["quantity"])

class DeckFormat(str, Enum):
    SIMPLE = "simple"
    MTGA = "mtga"
    MTGO = "mtgo"
    ARCHIDEKT = "archidekt"
    DECKSTATS = "deckstats"
    MOXFIELD = "moxfield"
    SCRYFALL_JSON = "scryfall_json"
    MPCFILL = "mpcfill"

def parse_deck(deck_text: str, format: DeckFormat, handle_card: Callable) -> None:
    if format == DeckFormat.SIMPLE:
        parse_simple_list(deck_text, handle_card)
    elif format == DeckFormat.MTGA:
        parse_mtga(deck_text, handle_card)
    elif format == DeckFormat.MTGO:
        parse_mtgo(deck_text, handle_card)
    elif format == DeckFormat.ARCHIDEKT:
        parse_archidekt(deck_text, handle_card)
    elif format == DeckFormat.DECKSTATS:
        parse_deckstats(deck_text, handle_card)
    elif format == DeckFormat.MOXFIELD:
        parse_moxfield(deck_text, handle_card)
    elif format == DeckFormat.SCRYFALL_JSON:
        parse_scryfall_json(deck_text, handle_card)
    elif format == DeckFormat.MPCFILL:
        parse_mpcfill(deck_text, handle_card)
    else:
        raise ValueError("Unrecognized deck format")