from os import path
from requests import Response, get
from time import sleep
from enum import Enum
from re import sub

ASHES_CARD_ART_URL_TEMPLATE = 'https://cdn.ashes.live/images/cards/{card_stub}.jpg'
ASHESDB_CARD_ART_URL_TEMPLATE = 'https://ashesdb-media.plaidhatgames.com/images/new-cards/{card_stub}.jpg'

class ImageServer(str, Enum):
    ASHES   = 'ashes'
    ASHESDB = 'ashesdb'

def request_ashes(query: str) -> Response:
    r = get(query, headers = {'user-agent': 'silhouette-card-maker/0.1', 'accept': '*/*'})

    r.raise_for_status()
    sleep(0.15)

    return r

def fetch_deck_data(deck_api_url: str):
    deck_response = request_ashes(deck_api_url)

    data = deck_response.json()

    phoenixborn = [data.get("phoenixborn")] or []
    main = data.get("cards") or []
    conjuration = data.get("conjurations") or []
    deck = phoenixborn + main + conjuration

    return deck

def fetch_card_art(index: int, card_name: str, card_stub: str, quantity: int, source: ImageServer, front_img_dir: str):
    url_template = ASHES_CARD_ART_URL_TEMPLATE
    if source == ImageServer.ASHESDB:
        url_template = ASHESDB_CARD_ART_URL_TEMPLATE
        card_stub = sub('-', '_', card_stub)
    
    card_art = request_ashes(url_template.format(card_stub=card_stub)).content

    if card_art is not None:
        # Save image based on quantity
        for counter in range(quantity):
            image_path = path.join(front_img_dir, f'{index}{card_name}_{counter + 1}.png')

            with open(image_path, 'wb') as f:
                f.write(card_art)

def get_handle_card(
    source: ImageServer,
    front_img_dir: str
):
    def configured_fetch_card(index: int, card_name: str, card_stub: str, quantity: int):
        fetch_card_art(
            index,
            card_name,
            card_stub,
            quantity,
            source,
            front_img_dir
        )

    return configured_fetch_card