import json
from html import unescape
from io import BytesIO
from os import path
from pathlib import Path
from re import compile, sub
from time import sleep
from unicodedata import category, normalize

from PIL import Image, ImageOps
from requests import Response, get

RINGSDB_BASE_URL = "https://ringsdb.com"
RINGSDB_ALL_CARDS_URL = f"{RINGSDB_BASE_URL}/api/public/cards/"
RINGSDB_CARD_URL_TEMPLATE = f"{RINGSDB_BASE_URL}/api/public/card/{{card_code}}.json"
RINGSDB_DECKLIST_URL_TEMPLATE = f"{RINGSDB_BASE_URL}/api/public/decklist/{{decklist_id}}.json"
RINGSDB_SCENARIO_URL_TEMPLATE = f"{RINGSDB_BASE_URL}/api/public/scenario/{{scenario_id}}.json"
RINGSDB_FELLOWSHIP_URL_TEMPLATE = f"{RINGSDB_BASE_URL}/fellowship/view/{{fellowship_id}}"
OUTPUT_CARD_ART_FILE_TEMPLATE = "{deck_index}_{card_code}_{card_name}_{quantity_counter}{extension}"
FELLOWSHIP_DECK_PATTERN = compile(r"Decks\[\d+\]\s*=\s*(\{.*?\});", flags=0)
FELLOWSHIP_NAME_PATTERN = compile(r"<h1[^>]*>(.*?)</h1>", flags=0)
PLUGIN_DIRECTORY = Path(__file__).resolve().parent


def request_ringsdb(query: str) -> Response:
    response = get(
        query,
        headers = {"user-agent": "silhouette-card-maker/0.1", "accept": "*/*"},
        timeout = 30,
    )
    response.raise_for_status()
    sleep(0.05)
    return response


def load_card_catalog() -> dict[str, dict]:
    cards = request_ringsdb(RINGSDB_ALL_CARDS_URL).json()
    return {card["code"]: card for card in cards if card.get("code")}


def fetch_card_details(card_code: str) -> dict:
    return request_ringsdb(RINGSDB_CARD_URL_TEMPLATE.format(card_code=card_code)).json()


def fetch_decklist(decklist_id: str) -> dict:
    return request_ringsdb(RINGSDB_DECKLIST_URL_TEMPLATE.format(decklist_id=decklist_id)).json()


def fetch_scenario_metadata(scenario_id: str) -> dict:
    return request_ringsdb(RINGSDB_SCENARIO_URL_TEMPLATE.format(scenario_id=scenario_id)).json()


def fetch_fellowship_decks(fellowship_id: str) -> tuple[str, list[dict]]:
    html = request_ringsdb(RINGSDB_FELLOWSHIP_URL_TEMPLATE.format(fellowship_id=fellowship_id)).text

    name_match = FELLOWSHIP_NAME_PATTERN.search(html)
    fellowship_name = (
        unescape(sub(r"<[^>]+>", "", name_match.group(1))).strip()
        if name_match
        else f"Fellowship {fellowship_id}"
    )

    decks = [json.loads(match.group(1)) for match in FELLOWSHIP_DECK_PATTERN.finditer(html)]
    return fellowship_name, decks


def sanitize_card_name(name: str) -> str:
    ascii_name = "".join(
        char for char in normalize("NFD", name) if category(char) != "Mn"
    )
    safe_name = sub(r"[^A-Za-z0-9 _-]+", "", ascii_name)
    collapsed = sub(r"\s+", "_", safe_name).strip("_")
    return collapsed or "card"


def sanitize_identifier(value: str) -> str:
    safe_value = sub(r"[^A-Za-z0-9_-]+", "_", value)
    collapsed = sub(r"_+", "_", safe_value).strip("_")
    return collapsed or "item"


def build_image_url(image_path: str | None) -> str | None:
    if not image_path:
        return None
    if image_path.startswith("http://") or image_path.startswith("https://"):
        return image_path
    return f"{RINGSDB_BASE_URL}{image_path}"


def normalize_card_orientation(card_art: bytes) -> bytes:
    with Image.open(BytesIO(card_art)) as image:
        image = ImageOps.exif_transpose(image)
        if image.width <= image.height:
            return card_art

        rotated = image.rotate(-90, expand=True)
        output = BytesIO()
        save_format = image.format or rotated.format or "PNG"
        rotated.save(output, format=save_format)
        return output.getvalue()


def iter_deck_slots(deck: dict) -> list[tuple[str, int]]:
    heroes = deck.get("heroes") or {}
    slots = deck.get("slots") or {}
    ordered_slots = []

    for card_code in heroes.keys():
        quantity = int(slots.get(card_code, heroes.get(card_code, 1)))
        ordered_slots.append((card_code, quantity))

    for card_code, quantity in slots.items():
        if card_code in heroes:
            continue
        ordered_slots.append((card_code, int(quantity)))

    return ordered_slots


def build_deck_entries(deck: dict, card_catalog: dict[str, dict]) -> list[dict]:
    entries = []

    for card_code, quantity in iter_deck_slots(deck):
        card = card_catalog.get(card_code)
        if card is None:
            card = fetch_card_details(card_code)

        image_url = build_image_url(card.get("imagesrc"))
        if image_url is None:
            print(f"Skipping card without image: {card_code}")
            continue

        entries.append(
            {
                "card_code": card_code,
                "name": card.get("name", card_code),
                "image_url": image_url,
                "quantity": quantity,
            }
        )

    return entries


def save_card_art_copies(
    card_art: bytes,
    output_dir: str,
    index: int,
    sanitized_code: str,
    sanitized_name: str,
    quantity: int,
    extension: str,
) -> None:
    for counter in range(quantity):
        output_filename = OUTPUT_CARD_ART_FILE_TEMPLATE.format(
            deck_index=str(index),
            card_code=sanitized_code,
            card_name=sanitized_name,
            quantity_counter=str(counter + 1),
            extension=extension,
        )
        image_path = path.join(output_dir, output_filename)
        with open(image_path, "wb") as file_handle:
            file_handle.write(card_art)


def fetch_card_art(
    index: int,
    quantity: int,
    sanitized_code: str,
    sanitized_name: str,
    image_url: str,
    extension: str,
    front_img_dir: str,
    double_sided_img_dir: str | None = None,
    back_image_url: str | None = None,
) -> None:
    # Fetch and normalize front image
    card_art = normalize_card_orientation(request_ringsdb(image_url).content)
    save_card_art_copies(
        card_art,
        front_img_dir,
        index,
        sanitized_code,
        sanitized_name,
        quantity,
        extension,
    )

    # Fetch and save back image if provided
    if back_image_url and double_sided_img_dir:
        back_art = normalize_card_orientation(request_ringsdb(back_image_url).content)
        back_extension = Path(back_image_url).suffix or extension
        save_card_art_copies(
            back_art,
            double_sided_img_dir,
            index,
            sanitized_code,
            sanitized_name,
            quantity,
            back_extension,
        )


def fetch_card(
    index: int,
    quantity: int,
    card_code: str,
    name: str,
    image_url: str,
    front_img_dir: str,
    double_sided_img_dir: str | None = None,
    back_image_url: str | None = None,
):
    extension = Path(image_url).suffix or ".png"
    sanitized_name = sanitize_card_name(name)
    sanitized_code = sanitize_identifier(card_code)

    fetch_card_art(
        index,
        quantity,
        sanitized_code,
        sanitized_name,
        image_url,
        extension,
        front_img_dir,
        double_sided_img_dir,
        back_image_url,
    )


def get_handle_card(front_img_dir: str, double_sided_img_dir: str | None = None):
    def configured_fetch_card(
        index: int,
        card_code: str,
        name: str,
        image_url: str,
        quantity: int = 1,
        back_image_url: str | None = None,
    ):
        fetch_card(
            index,
            quantity,
            card_code,
            name,
            image_url,
            front_img_dir,
            double_sided_img_dir,
            back_image_url,
        )

    return configured_fetch_card
