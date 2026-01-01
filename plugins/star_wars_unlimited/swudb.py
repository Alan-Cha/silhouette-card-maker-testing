from os import path
from requests import Response, get
from time import sleep
from re import sub, compile
from PIL import Image
from typing import Tuple

SWUDB_CARD_NUMBER_URL_TEMPLATE = 'https://api.swu-db.com/cards/{set_id}/{set_number}?format=json'
SWUDB_NAME_URL_TEMPLATE = 'https://swudb.com/api/search/{name}{title}?grouping=cards&sortorder=setno&sortdir=asc'
SWUDB_ART_URL_TEMPLATE = 'https://swudb.com/images/cards/{card_art_ref}'

OUTPUT_CARD_ART_FILE_TEMPLATE = '{deck_index}{card_name}{quantity_counter}.png'

card_tuple = Tuple[str, str] # Name, Title

def request_swudb(query: str) -> Response:
    r = get(query, headers = {'user-agent': 'silhouette-card-maker/0.1', 'accept': '*/*'})

    r.raise_for_status()
    sleep(0.15)

    return r

def fetch_name_and_title(card_id: str) -> card_tuple:
    card_id_pattern = compile(r'([A-Z]+)_(\d+)')
    card_name_dual_patten = compile(r'(.+) \/\/.+') # Chancellor Palpatine // Darth Sidious from TWI_017

    # Query for card name and title
    match = card_id_pattern.match(card_id)
    if match:
        set_id = match.group(1).strip().lower()
        set_number = int(match.group(2).strip())

        # Query for card name
        json = request_swudb(SWUDB_CARD_NUMBER_URL_TEMPLATE.format(set_id=set_id, set_number=set_number)).json()
        name = json.get('Name')
        name_match = card_name_dual_patten.match(name)
        if name_match:
            name = name_match.group(1).strip()

        title = json.get('Subtitle') or '' if json.get('Type') != 'Base' else ''

        # These are incorrectly hosted by swu-db
        if name == 'Darth Tyrannus':
            name = 'Darth Tyranus'
        if title == 'Darth Tyrannus':
            title = 'Darth Tyranus'

        return (name, title)
    
    else:
        raise Exception(f'Cannot parse card ID: "{card_id}"')

def fetch_card(
    index: int,
    quantity: int,
    name: str,
    title: str,
    front_img_dir: str,
    back_img_dir: str,
):
    # Fetch card art by querying name and title
    title_query = '' if title == '' else f' title:"{title}"'
    json = request_swudb(SWUDB_NAME_URL_TEMPLATE.format(name=name, title=title_query)).json()
    art_url_suffix = sub('.+cards/', '', json.get('printings')[0].get('frontImagePath'))
    front_art = request_swudb(SWUDB_ART_URL_TEMPLATE.format(card_art_ref=art_url_suffix)).content
    back_art = None

    # Get the back art from the path when card is not a Base
    if json.get('printings')[0].get('backImagePath') != '' and json.get('printings')[0].get('hp') is None:
        art_url_suffix = sub('.+cards/', '', json.get('printings')[0].get('backImagePath'))
        back_art = request_swudb(SWUDB_ART_URL_TEMPLATE.format(card_art_ref=art_url_suffix)).content

    # Save images based on quantity
    for counter in range(quantity):
        title_text = '' if title == '' else f',{title}'

        output_file = OUTPUT_CARD_ART_FILE_TEMPLATE.format(deck_index=str(index), card_name=f'{name}{title_text}', quantity_counter=str(counter + 1))

        if front_art != None:
            front_image_path = path.join(front_img_dir, output_file)

            with open(front_image_path, 'wb') as f:
                f.write(front_art)

            # Align the rotated art so that it has the correct orientation
            front_image_for_rotation = Image.open(front_image_path)
            if front_image_for_rotation.height < front_image_for_rotation.width:
                front_image_rotated = front_image_for_rotation.rotate(90, expand=True)
                front_image_rotated.save(front_image_path)

        if back_art != None:
            back_image_path = path.join(back_img_dir, output_file)

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
    def configured_fetch_card(index: int, name: str, title: str, quantity: int = 1):
        fetch_card(
            index,
            quantity,
            name,
            title,
            front_img_dir,
            back_img_dir
        )

    return configured_fetch_card
