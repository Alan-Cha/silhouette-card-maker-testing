from os import path
from requests import Response, get
from time import sleep
from re import sub
from PIL import Image

SWUDB_FRONT_ART_URL_TEMPLATE = 'https://swudb.com/images/cards/{card_number}.png'
SWUDB_BACK_ART_URL_TEMPLATE_1 = 'https://swudb.com/images/cards/{card_number}-back.png'
SWUDB_BACK_ART_URL_TEMPLATE_2 = 'https://swudb.com/images/cards/{card_number}-portrait.png'
SWUDB_NAME_URL_TEMPLATE = 'https://swudb.com/api/search/{name}{title}?grouping=cards&sortorder=setno&sortdir=asc'
SWUDB_ART_URL_TEMPLATE = 'https://swudb.com/images/cards/{card_art_ref}'

def ping_swudb(query: str) -> bool:
    r = get(query, headers = {'user-agent': 'silhouette-card-maker/0.1', 'accept': '*/*'})

    sleep(0.15)

    return False if r.status_code == 404 else True

def request_swudb(query: str) -> Response:
    r = get(query, headers = {'user-agent': 'silhouette-card-maker/0.1', 'accept': '*/*'})

    r.raise_for_status()
    sleep(0.15)

    return r

def fetch_card(
    index: int,
    quantity: int,
    name: str,
    title: str,
    card_number: str,
    front_img_dir: str,
    back_img_dir: str,
):
    # Query for card art
    if card_number != '': # Fetch card art by card number
        card_number_url_parse = sub('_', '/', card_number)
        front_art = request_swudb(SWUDB_FRONT_ART_URL_TEMPLATE.format(card_number=card_number_url_parse)).content
        back_art = None

        # Ping to verify the server has the back art in one of the possible naming formats, since we do not know if it does
        if ping_swudb(SWUDB_BACK_ART_URL_TEMPLATE_1.format(card_number=card_number_url_parse)) is True:
            back_art = request_swudb(SWUDB_BACK_ART_URL_TEMPLATE_1.format(card_number=card_number_url_parse)).content
        elif ping_swudb(SWUDB_BACK_ART_URL_TEMPLATE_2.format(card_number=card_number_url_parse)) is True:
            back_art = request_swudb(SWUDB_BACK_ART_URL_TEMPLATE_2.format(card_number=card_number_url_parse)).content
    else: # Fetch card art by querying name and title
        title_query = '' if title == '' else f' title:"{title}"'
        json = request_swudb(SWUDB_NAME_URL_TEMPLATE.format(name=name, title=title_query)).json()
        art_url_suffix = sub('.+cards/', '', json.get('variants')[0].get('frontImagePath'))
        front_art = request_swudb(SWUDB_ART_URL_TEMPLATE.format(card_art_ref=art_url_suffix)).content
        back_art = None

        # Get the back art from the path when the back portrait item is populated, since otherwise it could lead to a fake URL
        if json.get('variants')[0].get('backImagePath') != '' and json.get('variants')[0].get('isBackPortrait') is True:
            art_url_suffix = sub('.+cards/', '', json.get('variants')[0].get('backImagePath'))
            back_art = request_swudb(SWUDB_ART_URL_TEMPLATE.format(card_art_ref=art_url_suffix)).content
    
    # Save images based on quantity
    for counter in range(quantity):
        title_text = '' if title == '' else f',{title}'

        if front_art != None:
            if card_number == '':
                front_image_path = path.join(front_img_dir, f'{str(index)}{name}{title_text}{str(counter + 1)}.png')
            else:
                front_image_path = path.join(front_img_dir, f'{str(index)}{card_number}{str(counter + 1)}.png')

            with open(front_image_path, 'wb') as f:
                f.write(front_art)

            # Align the rotated art so that it has the correct orientation
            front_image_for_rotation = Image.open(front_image_path)
            if front_image_for_rotation.height < front_image_for_rotation.width:
                front_image_rotated = front_image_for_rotation.rotate(90, expand=True)
                front_image_rotated.save(front_image_path)  

        if back_art != None:
            if card_number == '':
                back_image_path = path.join(back_img_dir, f'{str(index)}{name}{title_text}{str(counter + 1)}.png')
            else:
                back_image_path = path.join(back_img_dir, f'{str(index)}{card_number}{str(counter + 1)}.png')

            with open(back_image_path, 'wb') as f:
                f.write(back_art)

            # Align the rotated art so that it has the correct orientation
            back_image_for_rotation = Image.open(back_image_path)
            if back_image_for_rotation.height < back_image_for_rotation.width:
                back_image_rotated = back_image_for_rotation.rotate(90, expand=True)
                back_image_rotated.save(back_image_path)

def get_handle_card(
    front_img_dir: str,
    back_img_dir: str,
):
    def configured_fetch_card(index: int, name: str, title: str, card_number: str, quantity: int = 1):
        fetch_card(
            index,
            quantity,
            name,
            title,
            card_number,
            front_img_dir,
            back_img_dir
        )

    return configured_fetch_card
    