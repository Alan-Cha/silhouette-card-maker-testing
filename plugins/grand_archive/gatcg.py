from re import sub
from os import path
from requests import Response, Session
from time import sleep

CARD_URL_TEMPLATE = 'https://api.gatcg.com/cards/{name}'
CARD_ART_URL_TEMPLATE = 'https://api.gatcg.com/{card_art_suffix}'

OUTPUT_CARD_ART_FILE_TEMPLATE = '{deck_index}{card_name}{quantity_counter}.png'

session = Session()

def request_gatcg(query: str) -> Response:
    r = session.get(query, headers = {'user-agent': 'silhouette-card-maker/0.1', 'accept': '*/*'})

    # Check for 2XX response code
    r.raise_for_status()

    sleep(0.075)

    return r

def fetch_card(
    index: int,
    quantity: int,
    card_name: str,
    front_img_dir: str,
):
    # Query for card info    
    sanitized = sub(r'[^A-Za-z0-9 \-]+', '', card_name)
    slugified = sub(r'\s+', '-', sanitized).lower()
    name_response = request_gatcg(CARD_URL_TEMPLATE.format(name=slugified))

    card_art_url = name_response.json().get('editions', [{}])[0].get('image')
    art_response = request_gatcg(CARD_ART_URL_TEMPLATE.format(card_art_suffix=card_art_url))
    
    if art_response is not None:
        card_art = art_response.content

        if card_art is not None:
            # Save image based on quantity
            for counter in range(quantity):
                image_path = path.join(front_img_dir, OUTPUT_CARD_ART_FILE_TEMPLATE.format(deck_index=str(index), card_name=card_name, quantity_counter=str(counter + 1)))

                with open(image_path, 'wb') as f:
                    f.write(card_art)

def get_handle_card(
    front_img_dir: str,
):
    def configured_fetch_card(index: int, card_name: str, quantity: int = 1):
        fetch_card(
            index,
            quantity,
            card_name,
            front_img_dir
        )

    return configured_fetch_card
    