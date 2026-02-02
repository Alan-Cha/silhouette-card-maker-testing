from os import path
from requests import get
from time import sleep
from json import dumps
import re

def remove_nonalphanumeric(s: str) -> str:
    return re.sub(r'[^\w]', '', s)

CURIOSA_DECK_URL_TEMPLATE = 'https://curiosa.io/decks/{deck_id}'
CURIOSA_DECK_API_URL = 'https://curiosa.io/api/trpc/deck.getDecklistById,deck.getAvatarById,deck.getSideboardById,deck.getMaybeboardById'

def get_cards(card_results, index: int):
      result = card_results[index].get('result', {}).get('data', {}).get('json', [])

      if isinstance(result, dict):
          return [result]
      return result

def get_curiosa_decklist(deck_id: str):
    deck_id = deck_id.strip()

    deck_payload = {
       '0': {'json': {'id': deck_id}},
       '1': {'json': {'id': deck_id}},
       '2': {'json': {'id': deck_id}},
       '3': {'json': {'id': deck_id}},
    }

    deck_params = { 'batch': '1', 'input': dumps(deck_payload)}

    headers = {'user-agent': 'silhouette-card-maker/0.1', 'accept': '*/*', 'referer': CURIOSA_DECK_URL_TEMPLATE.format(deck_id=deck_id)}

    r = get(CURIOSA_DECK_API_URL, params=deck_params, headers=headers)

    r.raise_for_status()
    sleep(0.15)

    deck_data = r.json()

    main   = get_cards(deck_data, 0)
    avatar = get_cards(deck_data, 1)
    side   = get_cards(deck_data, 2)
    maybe  = get_cards(deck_data, 3)

    decklist = []
    decklist.extend(main)
    decklist.extend(avatar)
    decklist.extend(side)
    decklist.extend(maybe)

    return decklist

def request_curiosa(query: str):

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
    card_art = request_curiosa(image_url).content
    clean_name = remove_nonalphanumeric(card_name)

    for counter in range(quantity):
        image_path = path.join(front_img_dir, f'{index}{clean_name}{counter + 1}.png')

        with open(image_path, 'wb') as f:
            f.write(card_art)

def get_handle_card(
    front_img_dir: str,
):
    def configured_fetch_card(index: int, card_name: str, image_url: str, quantity: int = 1):
        fetch_card(
            index,
            quantity,
            card_name,
            image_url,
            front_img_dir
        )

    return configured_fetch_card