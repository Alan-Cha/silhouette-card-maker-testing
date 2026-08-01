import os
from enum import Enum
from re import compile
from typing import Callable

from plugins.lotr_lcg.card_entry import CardEntry
from plugins.lotr_lcg.hallofbeorn import (
    ScenarioMode,
    fetch_all_scenarios,
    fetch_scenario_entries,
    find_scenario_slug,
    load_card_image_index,
)
from plugins.lotr_lcg.ringsdb import (
    build_deck_entries,
    fetch_decklist,
    fetch_fellowship_decks,
    fetch_scenario_metadata,
    load_card_catalog,
)

RINGSDB_URL_PATTERN = compile(
    r"https?://(?:www\.)?ringsdb\.com/decklist/view/(\d+)(?:/[^\s]*)?\s*$",
    flags=0,
)
RINGSDB_API_PATTERN = compile(
    r"https?://(?:www\.)?ringsdb\.com/api/public/decklist/(\d+)\.json\s*$",
    flags=0,
)
RINGSDB_FELLOWSHIP_URL_PATTERN = compile(
    r"https?://(?:www\.)?ringsdb\.com/fellowship/view/(\d+)(?:/[^\s]*)?\s*$",
    flags=0,
)
RINGSDB_SCENARIO_API_PATTERN = compile(
    r"https?://(?:www\.)?ringsdb\.com/api/public/scenario/(\d+)\.json\s*$",
    flags=0,
)
HALL_SCENARIO_URL_PATTERN = compile(
    r"https?://(?:www\.)?hallofbeorn\.com/LotR/Scenarios/([^\s/]+)\s*$",
    flags=0,
)
# Shared fallback for all RingsDB reference types: a bare numeric ID with no
# surrounding URL.
BARE_ID_PATTERN = compile(r"(\d+)\s*$")


def extract_decklist_id(value: str) -> str | None:
    line = value.strip()
    if not line:
        return None

    for pattern in (RINGSDB_URL_PATTERN, RINGSDB_API_PATTERN, BARE_ID_PATTERN):
        match = pattern.fullmatch(line)
        if match:
            return match.group(1)

    return None


def extract_fellowship_id(value: str) -> str | None:
    line = value.strip()
    if not line:
        return None

    for pattern in (RINGSDB_FELLOWSHIP_URL_PATTERN, BARE_ID_PATTERN):
        match = pattern.fullmatch(line)
        if match:
            return match.group(1)

    return None


def extract_ringsdb_scenario_id(value: str) -> str | None:
    line = value.strip()
    if not line:
        return None

    for pattern in (RINGSDB_SCENARIO_API_PATTERN, BARE_ID_PATTERN):
        match = pattern.fullmatch(line)
        if match:
            return match.group(1)

    return None


def extract_hallofbeorn_slug(value: str) -> str | None:
    line = value.strip()
    if not line:
        return None

    hall_match = HALL_SCENARIO_URL_PATTERN.fullmatch(line)
    if hall_match:
        return hall_match.group(1)

    return None


def read_reference_lines(deck_text: str) -> list[str]:
    """Read deck_text as a file if it is one, then split it into non-blank,
    stripped reference lines (URLs or bare IDs)."""
    if os.path.isfile(deck_text):
        with open(deck_text, "r", encoding="utf-8") as deck_file:
            deck_text = deck_file.read()

    return [line.strip() for line in deck_text.strip().split("\n") if line.strip()]


def emit_entries(entries: list[CardEntry], handle_card: Callable, index: int) -> tuple[int, list]:
    """
    Log and dispatch each CardEntry to handle_card. Card-level failures are
    caught and collected rather than raised, so one bad card doesn't stop the
    rest of the deck from being fetched.

    Returns the updated running index (so callers processing multiple
    batches, e.g. one fellowship's several decks, can keep counting across
    batches) and the list of (card_code, exception) pairs collected here.
    """
    errors = []

    for entry in entries:
        index += 1
        parts = [f"Index: {index}", f"quantity: {entry.quantity}"]
        if entry.name:
            parts.append(f"name: {entry.name}")
        if entry.card_code:
            parts.append(f"code: {entry.card_code}")
        print(", ".join(parts))

        try:
            handle_card(
                index,
                entry.card_code,
                entry.name,
                entry.image_url,
                entry.quantity,
                entry.back_image_url,
            )
        except Exception as exc:
            print(f"Error: {exc}")
            errors.append((entry.card_code, exc))

    return index, errors


def parse_ringsdb(deck_text: str, handle_card: Callable) -> None:
    """
    Parse RingsDB decklists using the JSON API.
    Uses: /api/public/decklist/{id}.json (pure JSON, no parsing needed)
    """
    card_catalog = load_card_catalog()
    index = 0
    errors = []

    for line in read_reference_lines(deck_text):
        deck_id = extract_decklist_id(line)
        if deck_id is None:
            print(f'Skipping: "{line}"')
            continue

        deck = fetch_decklist(deck_id)
        print(f'Deck: {deck.get("name", deck_id)} (ID: {deck_id})')

        index, batch_errors = emit_entries(build_deck_entries(deck, card_catalog), handle_card, index)
        errors.extend(batch_errors)

    if errors:
        print(f"Errors: {errors}")


def parse_ringsdb_fellowship(deck_text: str, handle_card: Callable) -> None:
    """
    Parse RingsDB fellowships by extracting JSON from JavaScript.
    Uses: /fellowship/view/{id} (HTML page with embedded JavaScript)
    Note: No fellowship JSON API exists, so we extract JSON from inline
    JavaScript variables like: Decks[0] = {...};
    """
    card_catalog = load_card_catalog()
    index = 0
    errors = []

    for line in read_reference_lines(deck_text):
        fellowship_id = extract_fellowship_id(line)
        if fellowship_id is None:
            print(f'Skipping: "{line}"')
            continue

        fellowship_name, decks = fetch_fellowship_decks(fellowship_id)
        print(f'Fellowship: {fellowship_name} (ID: {fellowship_id})')

        for deck in decks:
            print(f'  Deck: {deck.get("name", "Unnamed Deck")}')
            index, batch_errors = emit_entries(build_deck_entries(deck, card_catalog), handle_card, index)
            errors.extend(batch_errors)

    if errors:
        print(f"Errors: {errors}")


def parse_ringsdb_scenario_url(
    deck_text: str,
    handle_card: Callable,
    scenario_mode: str | ScenarioMode = ScenarioMode.NORMAL,
) -> None:
    """
    Parse RingsDB scenarios by fetching metadata, then looking up the
    matching scenario on Hall of Beorn by title.
    Uses: /api/public/scenario/{id}.json for metadata (name, pack, counts)
    Then: Hall of Beorn's /Export/Scenarios list (find_scenario_slug) to
    find that title's exact slug, and /Export/Scenarios/{slug} for the
    actual card list.

    RingsDB's scenario API has no card list, only metadata and aggregate
    counts, so the card data always comes from Hall of Beorn. Looking up the
    slug by title (rather than assuming RingsDB's nameCanonical equals Hall
    of Beorn's slug) avoids a real, confirmed mismatch: RingsDB's
    nameCanonical for scenario 1 is the lowercase "passage-through-mirkwood",
    but Hall of Beorn's actual slug is title-cased
    "Passage-Through-Mirkwood" -- a guess based on nameCanonical alone 404s.

    Hall of Beorn's scenario list and official card index are each fetched
    once here (not per line) and reused for every scenario reference in
    deck_text, since both are scenario-independent, multi-MB payloads.
    """
    index = 0
    errors = []
    scenarios = fetch_all_scenarios()
    card_image_index = load_card_image_index()

    for line in read_reference_lines(deck_text):
        scenario_id = extract_ringsdb_scenario_id(line)
        if scenario_id is None:
            print(f'Skipping: "{line}"')
            continue

        metadata = fetch_scenario_metadata(scenario_id)
        scenario_name = metadata.get("name", scenario_id)
        print(f"Scenario: {scenario_name} (ID: {scenario_id}, mode: {scenario_mode})")

        scenario_slug = find_scenario_slug(scenario_name, scenarios)
        if scenario_slug is None:
            raise ValueError(
                f'Could not find a Hall of Beorn scenario titled "{scenario_name}" (from RingsDB '
                f"scenario ID {scenario_id}). Find the scenario at https://hallofbeorn.com/LotR/Scenarios/ "
                f"and pass its URL directly with the hallofbeorn_url format instead."
            )

        entries = fetch_scenario_entries(scenario_slug, scenario_mode, scenarios, card_image_index)
        index, batch_errors = emit_entries(entries, handle_card, index)
        errors.extend(batch_errors)

    if errors:
        print(f"Errors: {errors}")


def parse_hallofbeorn_url(
    deck_text: str,
    handle_card: Callable,
    scenario_mode: str | ScenarioMode = ScenarioMode.NORMAL,
) -> None:
    """
    Parse Hall of Beorn scenarios directly by slug.
    Uses: Hall of Beorn's undocumented /Export/Scenarios/{slug} JSON API
    (see the module-level comment in hallofbeorn.py for details).
    `scenario_slug` here comes straight from a pasted /LotR/Scenarios/{slug}
    page URL, which uses the same slug the Export API expects.

    Hall of Beorn's scenario list and official card index are each fetched
    once here (not per line) and reused for every scenario reference in
    deck_text, since both are scenario-independent, multi-MB payloads.
    """
    index = 0
    errors = []
    scenarios = fetch_all_scenarios()
    card_image_index = load_card_image_index()

    for line in read_reference_lines(deck_text):
        scenario_slug = extract_hallofbeorn_slug(line)
        if scenario_slug is None:
            print(f'Skipping: "{line}"')
            continue

        print(f"Scenario: {scenario_slug} (mode: {scenario_mode})")

        entries = fetch_scenario_entries(scenario_slug, scenario_mode, scenarios, card_image_index)
        index, batch_errors = emit_entries(entries, handle_card, index)
        errors.extend(batch_errors)

    if errors:
        print(f"Errors: {errors}")


class DeckFormat(str, Enum):
    RINGSDB_URL = "ringsdb_url"
    RINGSDB_FELLOWSHIP_URL = "ringsdb_fellowship_url"
    RINGSDB_SCENARIO_URL = "ringsdb_scenario_url"
    HALLOFBEORN_URL = "hallofbeorn_url"


def parse_deck(
    deck_text: str,
    format: DeckFormat,
    handle_card: Callable,
    scenario_mode: str | ScenarioMode = ScenarioMode.NORMAL,
) -> None:
    if format == DeckFormat.RINGSDB_URL:
        return parse_ringsdb(deck_text, handle_card)
    if format == DeckFormat.RINGSDB_FELLOWSHIP_URL:
        return parse_ringsdb_fellowship(deck_text, handle_card)
    if format == DeckFormat.RINGSDB_SCENARIO_URL:
        return parse_ringsdb_scenario_url(deck_text, handle_card, scenario_mode)
    if format == DeckFormat.HALLOFBEORN_URL:
        return parse_hallofbeorn_url(deck_text, handle_card, scenario_mode)
    raise ValueError("Unrecognized deck format.")
