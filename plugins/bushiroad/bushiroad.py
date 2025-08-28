from os import path
from requests import Response, get
from time import sleep
from PIL import Image

DECK_API_URL = 'https://decklog-en.bushiroad.com/system/app/api/view/{deck_code}'

game_title_mapping = {
    '1': 'Cardfight Vanguard',
    '2': 'Weiss Schwarz',
    '6': 'Shadowverse: Evolve',
    '7': 'Godzilla',
    '8': 'Hololive',
}

game_image_url_mapping = {
    'Cardfight Vanguard': 'https://en.cf-vanguard.com/wordpress/wp-content/images/cardlist/{card_image}',
    'Weiss Schwarz': 'https://en.ws-tcg.com/wordpress/wp-content/images/cardimages/{card_image}',
    'Shadowverse: Evolve': 'https://en.shadowverse-evolve.com/wordpress/wp-content/images/cardlist/{card_image}',
    'Godzilla': 'https://en.godzilla-cardgame.com/wordpress/wp-content/images/cardlist/{card_image}',
    'Hololive': 'https://en.hololive-official-cardgame.com/wp-content/images/cardlist/{card_image}'
}

def request_bushiroad(query: str, referer: str = '') -> Response:
    if referer == '':
        r = get(query, headers = {'user-agent': 'silhouette-card-maker/0.1', 'accept': '*/*'})
    else:
        r = get(query, headers = {'user-agent': 'silhouette-card-maker/0.1', 'accept': '*/*', 'referer': referer})

    r.raise_for_status()
    sleep(0.15)

    return r

def fetch_decklist(deck_code: str):
    deck_request = request_bushiroad(DECK_API_URL.format(deck_code=deck_code), 'https://decklog-en.bushiroad.com/')
    json = deck_request.json()

    game_title = str(game_title_mapping.get(str(json.get('game_title_id'))))
    main_deck = json.get('list') or []
    leader = json.get('p_list') or []
    evolve_deck = json.get('sub_list') or []
    deck = leader + main_deck + evolve_deck

    return (game_title, deck)

def fetch_card(
    index: int,
    quantity: int,
    game_title: str,
    name: str,
    front_image: str,
    back_image: str,
    front_img_dir: str,
    back_img_dir: str
):
    # Query for card info
    image_url = game_image_url_mapping.get(game_title)
    front_card_art = request_bushiroad(image_url.format(card_image=front_image)).content
    back_card_art = None

    if back_image != '':
        back_card_art = request_bushiroad(image_url.format(card_image=back_image)).content

    for counter in range(quantity):

        if front_card_art is not None:
            front_image_path = path.join(front_img_dir, f'{str(index)}{name}{str(counter + 1)}.png')

            with open(front_image_path, 'wb') as f:
                f.write(front_card_art)
                
            # Align the rotated art so that it has the correct orientation
            front_image_for_rotation = Image.open(front_image_path)
            if front_image_for_rotation.height < front_image_for_rotation.width:
                front_image_rotated = front_image_for_rotation.rotate(-90, expand=True)
                front_image_rotated.save(front_image_path) 

        if back_card_art is not None:
            back_image_path = path.join(back_img_dir, f'{str(index)}{name}{str(counter + 1)}.png')

            with open(back_image_path, 'wb') as f:
                f.write(back_card_art)
                
            # Align the rotated art so that it has the correct orientation
            back_image_for_rotation = Image.open(back_image_path)
            if back_image_for_rotation.height < back_image_for_rotation.width:
                back_image_rotated = back_image_for_rotation.rotate(-90, expand=True)
                back_image_rotated.save(back_image_path)

def get_handle_card(
    front_img_dir: str,
    back_img_dir: str
):
    def configured_fetch_card(index: int, game_title: str, name: str, front_image: str, back_image: str, quantity = 1):
        fetch_card(
            index,
            quantity,
            game_title,
            name,
            front_image,
            back_image,
            front_img_dir,
            back_img_dir
        )

    return configured_fetch_card
