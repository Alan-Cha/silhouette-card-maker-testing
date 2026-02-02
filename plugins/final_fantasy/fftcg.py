from os import path
from requests import Response, get, post
from time import sleep

FFTCG_CARD_API_URL = 'https://fftcg.square-enix-games.com/na/get-cards'

def get_card_art_from_fftcg(card_name: str, serial_code: str) -> str:
    card_payload = {
        'language': 'en',
        'text': card_name,
        'type': [],
        'element': [],
        'cost': [],
        'rarity': [],
        'power': [],
        'category_1': [],
        'set': [],
        'multicard': '',
        'ex_burst': '',
        'code': serial_code,
        'special': '',
        'exactmatch': 1
    }
    r = post(FFTCG_CARD_API_URL, json=card_payload, headers = {'user-agent': 'silhouette-card-maker/0.1', 'accept': '*/*'})

    r.raise_for_status()
    sleep(0.15)

    cards = r.json().get('cards', [])
    if not cards:
        raise ValueError(f'Card not found: "{card_name}" (serial code: "{serial_code}")')

    return cards[0].get('images').get('full')[0]

def request_fftcg(query: str) -> Response:
    r = get(query, headers = {'user-agent': 'silhouette-card-maker/0.1', 'accept': '*/*'})

    r.raise_for_status()
    sleep(0.15)

    return r

def fetch_card(
    index: int,
    quantity: int,
    card_name: str,
    serial_code: str,
    front_img_dir: str,
):
    # Query for card info
    url = get_card_art_from_fftcg(card_name, serial_code)
    card_art = request_fftcg(url).content

    for counter in range(quantity):
        image_path = path.join(front_img_dir, f'{str(index)}{card_name}{str(counter + 1)}.png')

        with open(image_path, 'wb') as f:
            f.write(card_art)

def get_handle_card(
    front_img_dir: str,
):
    def configured_fetch_card(index: int, card_name: str, serial_code: str, quantity: int = 1):
        fetch_card(
            index,
            quantity,
            card_name,
            serial_code,
            front_img_dir
        )

    return configured_fetch_card