from os import path
from requests import Response, get
from time import sleep

DECK_ID_URL_TEMPLATE = 'https://play-api.carde.io/v1/decks/{deck_id}'

def request_elestrals(query: str) -> Response:
    r = get(query, headers = {'user-agent': 'silhouette-card-maker/0.1', 'accept': '*/*'})

    r.raise_for_status()
    sleep(0.15)

    return r

def fetch_deck_data(deck_id: str):
    deck_response = request_elestrals(DECK_ID_URL_TEMPLATE.format(deck_id=deck_id))

    data = deck_response.json().get("data")

    deck_section = data.get("deck").get("sections")
    deck = []
    for section in deck_section:
        deck += section.get("cards")

    card_section = data.get("cards")
    cards = {}
    for card in card_section:
        cards[card.get("_id")] = {
            "Name": card.get("name"),
            "Image": card.get("images").get("small")
        }

    return deck, cards

def fetch_card_art(index: int, card_name: str, image_url: str, quantity: int, front_img_dir: str):

    card_art = request_elestrals(image_url).content

    if card_art is not None:
        # Save image based on quantity
        for counter in range(quantity):
            image_path = path.join(front_img_dir, f'{index}{card_name}_{counter + 1}.jpg')

            with open(image_path, 'wb') as f:
                f.write(card_art)

def get_handle_card(
    front_img_dir: str
):
    def configured_fetch_card(index: int, card_name: str, image_url: str, quantity: int):
        fetch_card_art(
            index,
            card_name,
            image_url,
            quantity,
            front_img_dir
        )

    return configured_fetch_card