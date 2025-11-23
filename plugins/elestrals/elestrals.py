from io import BytesIO
from os import path
from requests import Response, get
from time import sleep
from PIL import Image

DECK_ID_URL_TEMPLATE = 'https://play-api.carde.io/v1/decks/{deck_id}'

def request_elestrals(query: str) -> Response:
    r = get(query, headers = {'user-agent': 'silhouette-card-maker/0.1', 'accept': '*/*'})

    r.raise_for_status()
    sleep(0.15)

    return r

def fetch_card_art(index: int, card_name: str, image_url: str, quantity: int, front_img_dir: str):
    response = request_elestrals(image_url)
    card_art_bytes = response.content

    if not card_art_bytes:
        raise Exception(f'Cannot fetch card art for "{card_name}"')

    # Load image from memory, no need to open a temporary file
    img = Image.open(BytesIO(card_art_bytes)).convert("RGBA")

    # Crop transparent bounding box if present
    transparent = img.getchannel("A")
    bbox = transparent.getbbox()
    if bbox:
        img = img.crop(bbox)

    # Save cropped image for each copy
    for counter in range(quantity):
        image_path = path.join(front_img_dir, f"{index}{card_name}_{counter + 1}.png")
        img.save(image_path, format="PNG")

def get_handle_card(
    front_img_dir: str
):
    def configured_fetch_card(index: int, card_name: str, image_url: str, quantity: int):
        fetch_card_art(
            index,
            card_name,
            image_url,
            quantity,
            front_img_dir
        )

    return configured_fetch_card