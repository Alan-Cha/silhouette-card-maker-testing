from os import path
from requests import Response, Session
from time import sleep
from re import sub
from .deck_formats import Pitch

# CardVault's card_id endpoint takes a deterministic slug rather than a search
# query: <slugified-name>[-<pitch value>]. E.g. "Energy Potion" at blue pitch
# (3) is 'energy-potion-3'. Cards without a pitch (weapons, equipment, heroes)
# use just the bare slug.
CARD_URL_TEMPLATE = 'https://api.cardvault.fabtcg.com/carddb/api/v1/card_id/{card_id}/'

OUTPUT_CARD_ART_FILE_TEMPLATE = '{deck_index}{card_name}{quantity_counter}.png'

session = Session()

def request_fabtcg(query: str) -> Response:
    r = session.get(query, headers = {'user-agent': 'silhouette-card-maker/0.1', 'accept': '*/*'})

    # Check for 2XX response code
    r.raise_for_status()

    sleep(0.075)

    return r

def build_card_id(name: str, pitch: Pitch) -> str:
    sanitized = sub(r'[^A-Za-z0-9 ]+', '', name)
    slug = sub(r'\s+', '-', sanitized.strip()).lower()

    if pitch != Pitch.NONE:
        slug = f'{slug}-{pitch.value}'

    return slug

def fetch_card(
    index: int,
    quantity: int,
    name: str,
    pitch: Pitch,
    front_img_dir: str,
):
    # Look up card info by its deterministic card_id
    sanitized = sub(r'[^A-Za-z0-9 ]+', '', name)
    card_id = build_card_id(name, pitch)

    url = CARD_URL_TEMPLATE.format(card_id=card_id)
    card_response = request_fabtcg(url)

    results = card_response.json().get('results') or []

    if not results:
        raise ValueError(f"CardVault returned no results for card_id '{card_id}' (name='{name}')")

    card_prints = results[0].get('card_prints') or []

    # Prefer the regular (non-foil) English printing; fall back to whatever's
    # first available if that specific combination isn't present.
    chosen_face = None

    for card_print in card_prints:
        for face in card_print.get('faces') or []:
            if face.get('face_language') == 'en' and face.get('finish_type') == 'regular':
                chosen_face = face
                break
        if chosen_face is not None:
            break

    if chosen_face is None:
        for card_print in card_prints:
            faces = card_print.get('faces') or []
            if faces:
                chosen_face = faces[0]
                break

    if chosen_face is None:
        raise ValueError(f"No printable face found for card_id '{card_id}' (name='{name}')")

    card_art_url = chosen_face.get('image', {}).get('normal')
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
