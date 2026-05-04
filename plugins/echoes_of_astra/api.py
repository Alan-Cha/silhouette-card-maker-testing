from os import path
from requests import Response, Session
from time import sleep
import re

ASTRA_DECK_URL_TEMPLATE = 'https://pphqxjttokwymgemkqvh.supabase.co/rest/v1/deck_cards?select=*&deck_id=eq.{deck_id}'
ASTRA_BUILDER_URL = 'https://www.astra-builder.com/en/create'

session = Session()

# Supabase public/anon key - this is intentionally public and safe to commit.
# It only provides read access to public decks via Row Level Security (RLS).
ASTRA_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBwaHF4anR0b2t3eW1nZW1rcXZoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTg3MzQ3OTcsImV4cCI6MjA3NDMxMDc5N30.z-xZSeC4Jl_s3EpeoCXfD8nl6Q4yDV6EohAgmsSUaS0'

_card_library = {}


def get_astra_deck(deck_id: str):
    global _card_library
    if not _card_library:
        r = session.get(ASTRA_BUILDER_URL, headers={'user-agent': 'silhouette-card-maker/0.1', 'accept': '*/*', 'RSC': '1'}, timeout=20)
        r.raise_for_status()
        for cid, name, img in re.findall(r'"id":"(IMP\d+)"[^}]*"name":"([^"]+)"[^}]*"imageSrc":"([^"]+)"', r.text):
            _card_library[cid] = {'name': name, 'image_url': img}
        if not _card_library:
            raise RuntimeError('Could not extract card library from Astra Builder')

    headers = {'user-agent': 'silhouette-card-maker/0.1', 'accept': '*/*', 'ApiKey': ASTRA_ANON_KEY}
    resp = session.get(ASTRA_DECK_URL_TEMPLATE.format(deck_id=deck_id), headers=headers, timeout=20)
    resp.raise_for_status()

    decklist = []
    for row in resp.json():
        info = _card_library.get(row.get('card_id'))
        if not info:
            continue
        decklist.append({'quantity': row.get('quantity'), 'cards': info})

    return decklist


def request_astra(query: str) -> Response:
    r = session.get(query, headers={'user-agent': 'silhouette-card-maker/0.1', 'accept': '*/*'})
    r.raise_for_status()
    sleep(0.075)
    return r


def remove_nonalphanumeric(s: str) -> str:
    return re.sub(r'[^\w]', '', s)


def fetch_card(index: int, quantity: int, card_name: str, image_url: str, front_img_dir: str):
    card_art = request_astra(image_url).content
    clean_card_name = remove_nonalphanumeric(card_name)
    for counter in range(quantity):
        image_path = path.join(front_img_dir, f'{str(index)}{clean_card_name}{str(counter + 1)}.png')
        with open(image_path, 'wb') as f:
            f.write(card_art)


def get_handle_card(front_img_dir: str):
    def configured_fetch_card(index: int, card_name: str, image_url: str, quantity: int = 1):
        fetch_card(index, quantity, card_name, image_url, front_img_dir)
    return configured_fetch_card
