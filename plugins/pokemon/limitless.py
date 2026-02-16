from os import path
from requests import Response, get
from requests.exceptions import HTTPError
from time import sleep
import filetype

LIMITLESS_TCG_URL_TEMPLATE = 'https://limitlesstcg.nyc3.cdn.digitaloceanspaces.com/tpci/{set_id}/{set_id}_{card_no}_R_EN_LG.png'
LIMITLESS_POCKET_URL_TEMPLATE = 'https://limitlesstcg.nyc3.cdn.digitaloceanspaces.com/pocket/{set_id}/{set_id}_{card_no}_EN_SM.webp'
# pokemontcg.io search API: queries by name/number and returns JSON with image
# URLs. Requires two requests (search + image download).
POKEMONTCG_API_URL = 'https://api.pokemontcg.io/v2/cards'
# pokemontcg.io images CDN: serves card images as static files. If you know
# the set ID and card number, you can download the image directly in one
# request without querying the API.
POKEMONTCG_IMAGE_URL_TEMPLATE = 'https://images.pokemontcg.io/{set_id}/{card_no}_hires.png'

# Static mapping from Limitless set codes to pokemontcg.io set IDs.
# The Limitless CDN only hosts images for HGSS-era sets (2010) and newer.
# Older sets use different set IDs on pokemontcg.io, so this mapping is needed
# to construct direct image URLs. This list is complete and will never need
# updating, since no new sets will be added to these older eras.
LIMITLESS_TO_POKEMONTCG_SET_ID = {
    # WotC era
    'BS': 'base1', 'JU': 'base2', 'FO': 'base3', 'BS2': 'base4',
    'TR': 'base5', 'G1': 'gym1', 'G2': 'gym2',
    'N1': 'neo1', 'N2': 'neo2', 'SI': 'si1', 'N3': 'neo3', 'N4': 'neo4',
    'LC': 'base6', 'E1': 'ecard1', 'E2': 'ecard2', 'E3': 'ecard3',
    'WP': 'basep', 'BG': 'bp',
    # EX era
    'RS': 'ex1', 'SS': 'ex2', 'DR': 'ex3', 'MA': 'ex4',
    'HL': 'ex5', 'RG': 'ex6', 'TRR': 'ex7', 'DX': 'ex8',
    'EM': 'ex9', 'UF': 'ex10', 'DS': 'ex11', 'LM': 'ex12',
    'HP': 'ex13', 'CG': 'ex14', 'DF': 'ex15', 'PK': 'ex16',
    'NP': 'np',
    'P1': 'pop1', 'P2': 'pop2', 'P3': 'pop3', 'P4': 'pop4', 'P5': 'pop5',
    # DP/Platinum era
    'DP': 'dp1', 'MT': 'dp2', 'SW': 'dp3', 'GE': 'dp4',
    'MD': 'dp5', 'LA': 'dp6', 'SF': 'dp7',
    'PL': 'pl1', 'RR': 'pl2', 'SV': 'pl3', 'AR': 'pl4',
    'RM': 'ru1',
    'P6': 'pop6', 'P7': 'pop7', 'P8': 'pop8', 'P9': 'pop9',
}

_failed_tcg_sets = set()
_failed_pocket_sets = set()

def request_limitless(query: str) -> Response:
    r = get(query, headers = {'user-agent': 'silhouette-card-maker/0.1', 'accept': '*/*'})

    # Check for 2XX response code
    r.raise_for_status()

    sleep(0.075)

    return r

def request_pokemontcg(url: str, params: dict = None) -> Response:
    r = get(url, params=params, headers = {'user-agent': 'silhouette-card-maker/0.1', 'accept': '*/*'})

    # Check for 2XX response code
    r.raise_for_status()

    sleep(0.075)

    return r

def fetch_card_from_pokemontcg(card_name: str, card_number: str) -> bytes:
    search_query = f'name:"{card_name}" number:{card_number}'
    response = request_pokemontcg(POKEMONTCG_API_URL, params={'q': search_query})
    data = response.json()

    cards = data.get('data', [])
    if not cards:
        raise Exception(f'No results found on pokemontcg.io for "{card_name}" number {card_number}')

    card = cards[0]
    image_url = card.get('images', {}).get('large')
    if not image_url:
        raise Exception(f'No large image available on pokemontcg.io for "{card_name}" number {card_number}')

    return request_pokemontcg(image_url).content

def fetch_card(
    index: int,
    quantity: int,
    card_name: str,
    set_id: str,
    card_number: str,
    front_img_dir: str,
):
    card_art = None

    # Try Pokemon TCG format first
    if set_id not in _failed_tcg_sets:
        try:
            url = LIMITLESS_TCG_URL_TEMPLATE.format(set_id=set_id, card_no=str(card_number).zfill(3))
            card_art = request_limitless(url).content
        except HTTPError:
            _failed_tcg_sets.add(set_id)

    # Fall back to Pokemon Pocket format
    if card_art is None and set_id not in _failed_pocket_sets:
        try:
            url = LIMITLESS_POCKET_URL_TEMPLATE.format(set_id=set_id, card_no=str(card_number).zfill(3))
            card_art = request_limitless(url).content
        except HTTPError:
            _failed_pocket_sets.add(set_id)

    # Fall back to pokemontcg.io images CDN (for older pre-HGSS sets not on
    # the Limitless CDN). Downloads the image directly without an API query.
    if card_art is None and set_id in LIMITLESS_TO_POKEMONTCG_SET_ID:
        try:
            pokemontcg_set_id = LIMITLESS_TO_POKEMONTCG_SET_ID[set_id]
            url = POKEMONTCG_IMAGE_URL_TEMPLATE.format(set_id=pokemontcg_set_id, card_no=card_number)
            card_art = request_pokemontcg(url).content
        except HTTPError:
            pass

    # Fall back to pokemontcg.io search API (queries by name/number)
    if card_art is None:
        try:
            card_art = fetch_card_from_pokemontcg(card_name, card_number)
        except Exception as e:
            raise Exception(f'Failed to fetch card "{card_name}" (set: {set_id}, number: {card_number}): {e}')

    file_ext = filetype.guess(card_art).extension

    for counter in range(quantity):
        image_path = path.join(front_img_dir, f'{str(index)}{card_name}{str(counter + 1)}.{file_ext}')

        with open(image_path, 'wb') as f:
            f.write(card_art)

def get_handle_card(
    front_img_dir: str,
):
    def configured_fetch_card(index: int, card_name: str, set_id: str, card_number: str, quantity: int = 1):
        fetch_card(
            index,
            quantity,
            card_name,
            set_id,
            card_number,
            front_img_dir
        )

    return configured_fetch_card