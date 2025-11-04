from os import path
from re import compile, search, sub
from enum import Enum
import time
import requests

PILTOVER_URL_TEMPLATE = 'https://cdn.piltoverarchive.com/cards/{card_number}.webp'
RIFTMANA_URL_TEMPLATE = 'https://riftmana.com/wp-content/uploads/Cards/{card_number}.webp'

class ImageServer(str, Enum):
    PILTOVER = 'piltover_archive'
    RIFTMANA = 'riftmana'

def request_api(query: str) -> requests.Response:
    r = requests.get(query, headers = {'user-agent': 'silhouette-card-maker/0.1', 'accept': '*/*'})
    r.raise_for_status()
    time.sleep(0.15)

    return r

def fetch_card_art(index: int, card_number: str, quantity: int, source: ImageServer, front_img_dir: str):
    url_template = PILTOVER_URL_TEMPLATE
    if source == ImageServer.RIFTMANA:
        url_template = RIFTMANA_URL_TEMPLATE

    image_server_query = url_template.format(card_number=card_number)
    api_response = request_api(image_server_query)

    # Otherwise, try to retrieve the art for the signature art of the card since the request failed for alternate art
    if api_response is None:
        alternate_art_suffix_pattern = compile(r'^([A-Z0-9]+-\d+)a$')
        match = search(alternate_art_suffix_pattern, card_number)
        if match:
            image_server_query = url_template.format(card_number=f'{match.group(1)}s')
            api_response = request_api(image_server_query)

    if api_response is not None:
        card_art = api_response.content

        if card_art is not None:
            # Save image based on quantity
            for counter in range(quantity):
                image_path = path.join(front_img_dir, f'{index}{card_number}_{counter + 1}.jpg')

                with open(image_path, 'wb') as f:
                    f.write(card_art)

def fetch_card_number(name: str) -> str:
    # Edge case of cards that are misnamed on the backend
    if name == "Spirit's Refuge":
        name = "Spirit's Rifuge"

    # Get the internal information based on the card name to route to the card itself
    sanitized = sub(r'[^A-Za-z0-9 \-]+', '', name)
    slugified = sub(r'\s+', '-', sanitized).lower()

    url = f"https://riftmana.com/wp-json/wp/v2/card-name?search={slugified}"
    name_response = request_api(url)

    # Now we can retrieve the card number
    card_link = name_response.json()[0].get('_links', {}).get('wp:post_type')[0].get('href')
    card_response = request_api(card_link)
    card_number_and_name = card_response.json()[0].get('title').get('rendered')

    # '{Card Number} {Card Name}'
    pattern = compile(r'^([A-Z0-9]+-\d+[a-z]?)(\s+|-)(.*)$')
    match = pattern.match(card_number_and_name)

    if match:
        return match.group(1).strip()

def get_handle_card(
    source: ImageServer,
    front_img_dir: str
):
    def configured_fetch_card(index: int, card_number: str, quantity: int):
        fetch_card_art(
            index,
            card_number,
            quantity,
            source,
            front_img_dir
        )

    return configured_fetch_card
