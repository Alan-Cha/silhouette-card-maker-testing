from os import path
from requests import Response, get
from time import sleep
from re import sub
from .deck_formats import Pitch

CARD_URL_TEMPLATE = 'https://cards.fabtcg.com/api/search/v1/cards/?name={card_name}{pitch}'

OUTPUT_CARD_ART_FILE_TEMPLATE = '{deck_index}{card_name}{quantity_counter}.png'

def request_fabtcg(query: str) -> Response:
    r = get(query, headers = {'user-agent': 'silhouette-card-maker/0.1', 'accept': '*/*'})

    # Check for 2XX response code
    r.raise_for_status()

    sleep(0.075)

    return r

def fetch_card(
    index: int,
    quantity: int,
    name: str,
    pitch: Pitch,
    front_img_dir: str,
):
    # Query for card info
    sanitized = sub(r'[^A-Za-z0-9 ]+', '', name)
    slugified = sub(r'\s+', '+', sanitized).lower()
    pitch_argument = f'&pitch_lookup=exact&pitch={pitch.value}' if pitch != Pitch.NONE else ''

    url = CARD_URL_TEMPLATE.format(card_name=slugified,pitch=pitch_argument)
    card_response = request_fabtcg(url)

    card_art_url = card_response.json().get('results')[0].get('image').get('normal')
    card_art_response = request_fabtcg(card_art_url)

    if card_art_response is not None:
        card_art = card_art_response.content

        if card_art is not None:
            # Save image based on quantity
            for counter in range(quantity):
                image_path = path.join(front_img_dir, OUTPUT_CARD_ART_FILE_TEMPLATE.format(deck_index=str(index), card_name=sanitized, quantity_counter=str(counter+1)))

                with open(image_path, 'wb') as f:
                    f.write(card_art)

def get_handle_card(
    front_img_dir: str,
):
    def configured_fetch_card(index: int, name: str, pitch: Pitch, quantity: int = 1):
        fetch_card(
            index,
            quantity,
            name,
            pitch,
            front_img_dir
        )

    return configured_fetch_card
