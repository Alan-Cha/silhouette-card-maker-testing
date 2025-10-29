from os import path
from requests import Response, get
from time import sleep

LIMITLESS_TCG_URL_TEMPLATE = 'https://limitlesstcg.nyc3.cdn.digitaloceanspaces.com/tpci/{set_id}/{set_id}_{card_no}_R_EN_LG.png'
LIMITLESS_POCKET_URL_TEMPLATE = 'https://limitlesstcg.nyc3.cdn.digitaloceanspaces.com/pocket/{set_id}/{set_id}_{card_no}_EN_SM.webp'

def request_limitless(query: str) -> Response:
    r = get(query, headers = {'user-agent': 'silhouette-card-maker/0.1', 'accept': '*/*'})

    r.raise_for_status()
    sleep(0.15)

    return r

def fetch_card(
    index: int,
    quantity: int,
    card_name: str,
    set_id: str,
    card_number: int,
    front_img_dir: str,
):
    # Query for card info
    url = ''
    card_art = None

    try:
        url = LIMITLESS_TCG_URL_TEMPLATE.format(set_id=set_id, card_no=str(card_number).zfill(3)) # This format supports Pokemon TCG
        card_art = request_limitless(url).content
    except:
        url = LIMITLESS_POCKET_URL_TEMPLATE.format(set_id=set_id, card_no=str(card_number).zfill(3)) # This format supports Pokemon Pocket
        card_art = request_limitless(url).content

    for counter in range(quantity):
        image_path = path.join(front_img_dir, f'{str(index)}{card_name}{str(counter + 1)}.png')

        with open(image_path, 'wb') as f:
            f.write(card_art)

def get_handle_card(
    front_img_dir: str,
):
    def configured_fetch_card(index: int, card_name: str, set_id: str, card_number: int, quantity: int = 1):
        fetch_card(
            index,
            quantity,
            card_name,
            set_id,
            card_number,
            front_img_dir
        )

    return configured_fetch_card