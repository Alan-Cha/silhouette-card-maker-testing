from os import path
from requests import Response, get, post
from time import sleep

FFTCG_CARD_API_URL = 'https://fftcg.square-enix-games.com/na/get-cards'

def get_card_art_from_fftcg(card_name: str, serial_code: str, category: str = '') -> str:
    card_payload = {
        'language': 'en',
        'text': card_name,
        'type': [],
        'element': [],
        'cost': [],
        'rarity': [],
        'power': [],
        'category_1': [category] if category else [],
        'set': [],
        'multicard': '',
        'ex_burst': '',
        'code': serial_code,
        'special': '',
        'exactmatch': 1
    }
    r = post(FFTCG_CARD_API_URL, json=card_payload, headers = {'user-agent': 'silhouette-card-maker/0.1', 'accept': '*/*'})

    # Check for 2XX response code
    r.raise_for_status()

    sleep(0.075)

    cards = r.json().get('cards', [])
    if not cards:
        details = [f'name: "{card_name}"']
        if serial_code:
            details.append(f'serial code: "{serial_code}"')
        if category:
            details.append(f'category: "{category}"')
        raise ValueError(f'Card not found ({", ".join(details)})')

    return cards[0].get('images').get('full')[0]

def request_fftcg(query: str) -> Response:
    r = get(query, headers = {'user-agent': 'silhouette-card-maker/0.1', 'accept': '*/*'})

    # Check for 2XX response code
    r.raise_for_status()

    sleep(0.075)

    return r

def fetch_card(
    index: int,
    quantity: int,
    card_name: str,
    serial_code: str,
    front_img_dir: str,
    category: str = '',
):
    # Query for card info
    url = get_card_art_from_fftcg(card_name, serial_code, category)
    card_art = request_fftcg(url).content

    for counter in range(quantity):
        image_path = path.join(front_img_dir, f'{str(index)}{card_name}{str(counter + 1)}.png')

        with open(image_path, 'wb') as f:
            f.write(card_art)

def get_handle_card(
    front_img_dir: str,
):
    def configured_fetch_card(index: int, card_name: str, serial_code: str, quantity: int = 1, category: str = ''):
        fetch_card(
            index,
            quantity,
            card_name,
            serial_code,
            front_img_dir,
            category
        )

    return configured_fetch_card