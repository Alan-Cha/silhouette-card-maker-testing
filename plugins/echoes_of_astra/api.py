from os import path
from requests import Response, get
from time import sleep

ASTRA_DECK_URL_TEMPLATE = 'https://pphqxjttokwymgemkqvh.supabase.co/rest/v1/decks?select=id,is_public,deck_cards(quantity,cards(*))&id=eq.{deck_id}'

def get_astra_deck(deck_id: str):
       
    headers = {
        'user-agent': 'silhouette-card-maker/0.1', 'accept': '*/*',
        'ApiKey': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBwaHF4anR0b2t3eW1nZW1rcXZoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTg3MzQ3OTcsImV4cCI6MjA3NDMxMDc5N30.z-xZSeC4Jl_s3EpeoCXfD8nl6Q4yDV6EohAgmsSUaS0'
    }

    url = ASTRA_DECK_URL_TEMPLATE.format(deck_id=deck_id)
    resp = get(url, headers=headers, timeout=20)
    resp.raise_for_status()
    data = resp.json()

    decklist = data[0].get('deck_cards', [])

    return decklist

def request_astra(query: str) -> Response:
    r = get(query, headers = {'user-agent': 'silhouette-card-maker/0.1', 'accept': '*/*'})

    r.raise_for_status()
    sleep(0.15)

    return r

def fetch_card(
    index: int,
    quantity: int,
    card_name: str,
    image_url: str,
    front_img_dir: str,
):
    # Query for card info
    card_art = request_astra(image_url).content

    for counter in range(quantity):
        image_path = path.join(front_img_dir, f'{str(index)}{card_name}{str(counter + 1)}.png')

        with open(image_path, 'wb') as f:
            f.write(card_art)

def get_handle_card(
    front_img_dir: str,
):
    def configured_fetch_card(index: int, card_name: str, image_url: int, quantity: int = 1):
        fetch_card(
            index,
            quantity,
            card_name,
            image_url,
            front_img_dir
        )

    return configured_fetch_card
