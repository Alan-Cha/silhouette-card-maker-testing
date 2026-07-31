import os
from io import BytesIO
from re import sub
from time import sleep

import requests
from PIL import Image

API_BASE = 'https://arkhamdb.com/api/public'
IMAGE_URL_TEMPLATE = 'https://arkhamdb.com{image_path}'

session = requests.Session()

def request_arkhamdb(query: str) -> requests.Response:
    r = session.get(query, headers={'user-agent': 'silhouette-card-maker/0.1', 'accept': '*/*'})

    # Check for 2XX response code
    r.raise_for_status()

    sleep(0.075)

    return r

def fetch_arkhamdb_deck(deck_id: str, is_decklist: bool) -> dict:
    key = 'decklist' if is_decklist else 'deck'
    return request_arkhamdb(f'{API_BASE}/{key}/{deck_id}.json').json()

def fetch_card_json(code: str) -> dict:
    return request_arkhamdb(f'{API_BASE}/card/{code}.json').json()

def remove_nonalphanumeric(s: str) -> str:
    return sub(r'[^\w]', '', s)

def prepare_card_image(image_bytes: bytes) -> Image.Image:
    img = Image.open(BytesIO(image_bytes))

    # Acts, agendas, and some encounter cards are printed landscape but
    # need to be laid out portrait alongside the rest of the deck.
    if img.width > img.height:
        img = img.rotate(-90, expand=True)

    return img

def fetch_card_art(
    index: int,
    code: str,
    quantity: int,
    front_img_dir: str,
    double_sided_dir: str,
) -> None:
    card = fetch_card_json(code)

    name = card.get('name') or code
    clean_name = remove_nonalphanumeric(name)

    front_path = card.get('imagesrc')
    if not front_path:
        raise ValueError(f'No image available for card "{code}"')

    front_img = prepare_card_image(request_arkhamdb(IMAGE_URL_TEMPLATE.format(image_path=front_path)).content)
    for counter in range(quantity):
        image_path = os.path.join(front_img_dir, f'{index}{clean_name}{counter + 1}.png')
        front_img.save(image_path)

    # Double-sided cards either carry their own back image (investigators,
    # some player cards) or link out to a separate card entry that holds it
    # (many encounter cards).
    back_path = card.get('backimagesrc')
    if not back_path:
        linked_card = card.get('linked_card')
        if linked_card:
            back_path = linked_card.get('imagesrc')

    if back_path:
        back_img = prepare_card_image(request_arkhamdb(IMAGE_URL_TEMPLATE.format(image_path=back_path)).content)
        for counter in range(quantity):
            image_path = os.path.join(double_sided_dir, f'{index}{clean_name}{counter + 1}.png')
            back_img.save(image_path)

def get_handle_card(front_img_dir: str, double_sided_dir: str):
    def configured_fetch_card(index: int, code: str, quantity: int):
        fetch_card_art(
            index,
            code,
            quantity,
            front_img_dir,
            double_sided_dir,
        )

    return configured_fetch_card
