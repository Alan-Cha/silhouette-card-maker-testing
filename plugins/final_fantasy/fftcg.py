from os import path
from requests import Response, get
from time import sleep

FFTCG_CARD_ART_TEMPLATE = 'https://fftcg.cdn.sewest.net/images/cards/full/{serial_code}_eg.jpg'

def request_fftcg(query: str) -> Response:
    r = get(query, headers = {'user-agent': 'silhouette-card-maker/0.1', 'accept': '*/*'})

    r.raise_for_status()
    sleep(0.15)

    return r

def fetch_card(
    index: int,
    quantity: int,
    card_name: str,
    serial_code: int,
    front_img_dir: str,
):
    # Query for card info
    url = FFTCG_CARD_ART_TEMPLATE.format(serial_code=serial_code)
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