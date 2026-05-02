import os
from enum import Enum
from re import compile
from typing import Callable

from plugins.lotr_lcg.hallofbeorn import fetch_scenario_entries
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
RINGSDB_ID_PATTERN = compile(r"(\d+)\s*$")
RINGSDB_FELLOWSHIP_URL_PATTERN = compile(
    r"https?://(?:www\.)?ringsdb\.com/fellowship/view/(\d+)(?:/[^\s]*)?\s*$",
    flags=0,
)
RINGSDB_FELLOWSHIP_ID_PATTERN = compile(r"(\d+)\s*$")
RINGSDB_SCENARIO_API_PATTERN = compile(
    r"https?://(?:www\.)?ringsdb\.com/api/public/scenario/(\d+)\.json\s*$",
    flags=0,
)
HALL_SCENARIO_URL_PATTERN = compile(
    r"https?://(?:www\.)?hallofbeorn\.com/LotR/Scenarios/([^\s/]+)\s*$",
    flags=0,
)
RINGSDB_SCENARIO_ID_PATTERN = compile(r"(\d+)\s*$")


def extract_decklist_id(value: str) -> str | None:
    line = value.strip()
    if not line:
        return None

    for pattern in (RINGSDB_URL_PATTERN, RINGSDB_API_PATTERN, RINGSDB_ID_PATTERN):
        match = pattern.fullmatch(line)
        if match:
            return match.group(1)

    return None


def extract_fellowship_id(value: str) -> str | None:
    line = value.strip()
    if not line:
        return None

    for pattern in (RINGSDB_FELLOWSHIP_URL_PATTERN, RINGSDB_FELLOWSHIP_ID_PATTERN):
        match = pattern.fullmatch(line)
        if match:
            return match.group(1)

    return None


def extract_ringsdb_scenario_id(value: str) -> str | None:
    line = value.strip()
    if not line:
        return None

    for pattern in (RINGSDB_SCENARIO_API_PATTERN, RINGSDB_SCENARIO_ID_PATTERN):
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


def parse_ringsdb(deck_text: str, handle_card: Callable) -> None:
    if os.path.isfile(deck_text):
        with open(deck_text, "r", encoding="utf-8") as deck_file:
            deck_text = deck_file.read()

    card_catalog = load_card_catalog()
    error_lines = []
    index = 0

    for line in deck_text.strip().split("\n"):
        line = line.strip()
        if not line:
            continue

        deck_id = extract_decklist_id(line)
        if deck_id is None:
            print(f'Skipping: "{line}"')
            continue

        deck = fetch_decklist(deck_id)
        print(f'Deck: {deck.get("name", deck_id)} (ID: {deck_id})')

        for entry in build_deck_entries(deck, card_catalog):
            index += 1
            parts = [f"Index: {index}", f'quantity: {entry["quantity"]}']
            if entry["name"]:
                parts.append(f'name: {entry["name"]}')
            if entry["card_code"]:
                parts.append(f'code: {entry["card_code"]}')
            print(", ".join(parts))

            try:
                handle_card(
                    index,
                    entry["card_code"],
                    entry["name"],
                    entry["image_url"],
                    entry["quantity"],
                    None,
                )
            except Exception as exc:
                print(f"Error: {exc}")
                error_lines.append((entry["card_code"], exc))

    if len(error_lines) > 0:
        print(f"Errors: {error_lines}")


def parse_ringsdb_fellowship(deck_text: str, handle_card: Callable) -> None:
    if os.path.isfile(deck_text):
        with open(deck_text, "r", encoding="utf-8") as deck_file:
            deck_text = deck_file.read()

    card_catalog = load_card_catalog()
    error_lines = []
    index = 0

    for line in deck_text.strip().split("\n"):
        line = line.strip()
        if not line:
            continue

        fellowship_id = extract_fellowship_id(line)
        if fellowship_id is None:
            print(f'Skipping: "{line}"')
            continue

        fellowship_name, decks = fetch_fellowship_decks(fellowship_id)
        print(f'Fellowship: {fellowship_name} (ID: {fellowship_id})')

        for deck in decks:
            print(f'  Deck: {deck.get("name", "Unnamed Deck")}')
            for entry in build_deck_entries(deck, card_catalog):
                index += 1
                parts = [f"Index: {index}", f'quantity: {entry["quantity"]}']
                if entry["name"]:
                    parts.append(f'name: {entry["name"]}')
                if entry["card_code"]:
                    parts.append(f'code: {entry["card_code"]}')
                print(", ".join(parts))

                try:
                    handle_card(
                        index,
                        entry["card_code"],
                        entry["name"],
                        entry["image_url"],
                        entry["quantity"],
                        None,
                    )
                except Exception as exc:
                    print(f"Error: {exc}")
                    error_lines.append((entry["card_code"], exc))

    if len(error_lines) > 0:
        print(f"Errors: {error_lines}")


def parse_ringsdb_scenario_url(
    deck_text: str,
    handle_card: Callable,
    scenario_mode: str = "normal",
) -> None:
    if os.path.isfile(deck_text):
        with open(deck_text, "r", encoding="utf-8") as deck_file:
            deck_text = deck_file.read()

    error_lines = []
    index = 0

    for line in deck_text.strip().split("\n"):
        line = line.strip()
        if not line:
            continue

        scenario_id = extract_ringsdb_scenario_id(line)
        if scenario_id is None:
            print(f'Skipping: "{line}"')
            continue

        metadata = fetch_scenario_metadata(scenario_id)
        scenario_slug = metadata.get("nameCanonical")
        scenario_name = metadata.get("name", scenario_id)
        print(f"Scenario: {scenario_name} (ID: {scenario_id}, mode: {scenario_mode})")

        for entry in fetch_scenario_entries(scenario_slug, scenario_mode):
            index += 1
            parts = [f"Index: {index}", f'quantity: {entry["quantity"]}']
            if entry["name"]:
                parts.append(f'name: {entry["name"]}')
            print(", ".join(parts))

            try:
                handle_card(
                    index,
                    entry["card_code"],
                    entry["name"],
                    entry["image_url"],
                    entry["quantity"],
                    entry.get("back_image_url"),
                )
            except Exception as exc:
                print(f"Error: {exc}")
                error_lines.append((entry["card_code"], exc))

    if len(error_lines) > 0:
        print(f"Errors: {error_lines}")


def parse_hallofbeorn_url(
    deck_text: str,
    handle_card: Callable,
    scenario_mode: str = "normal",
) -> None:
    if os.path.isfile(deck_text):
        with open(deck_text, "r", encoding="utf-8") as deck_file:
            deck_text = deck_file.read()

    error_lines = []
    index = 0

    for line in deck_text.strip().split("\n"):
        line = line.strip()
        if not line:
            continue

        scenario_slug = extract_hallofbeorn_slug(line)
        if scenario_slug is None:
            print(f'Skipping: "{line}"')
            continue

        print(f"Scenario: {scenario_slug} (mode: {scenario_mode})")

        for entry in fetch_scenario_entries(scenario_slug, scenario_mode):
            index += 1
            parts = [f"Index: {index}", f'quantity: {entry["quantity"]}']
            if entry["name"]:
                parts.append(f'name: {entry["name"]}')
            print(", ".join(parts))

            try:
                handle_card(
                    index,
                    entry["card_code"],
                    entry["name"],
                    entry["image_url"],
                    entry["quantity"],
                    entry.get("back_image_url"),
                )
            except Exception as exc:
                print(f"Error: {exc}")
                error_lines.append((entry["card_code"], exc))

    if len(error_lines) > 0:
        print(f"Errors: {error_lines}")


class DeckFormat(str, Enum):
    RINGSDB_URL = "ringsdb_url"
    RINGSDB_FELLOWSHIP_URL = "ringsdb_fellowship_url"
    RINGSDB_SCENARIO_URL = "ringsdb_scenario_url"
    HALLOFBEORN_URL = "hallofbeorn_url"


def parse_deck(
    deck_text: str,
    format: DeckFormat,
    handle_card: Callable,
    scenario_mode: str = "normal",
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
