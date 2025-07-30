from os import path
from requests import Response, get
from time import sleep
from re import sub

def ping_swudb(query: str) -> bool:
    r = get(query, headers = {'user-agent': 'silhouette-card-maker/0.1', 'accept': '*/*'})

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
    # Query for card info
    if card_number != '':
        card_number_url_parse = sub('_', '/', card_number)
        front_art = request_swudb(f'https://swudb.com/images/cards/{card_number_url_parse}.png').content
        back_art = None
        if ping_swudb(f'https://swudb.com/images/cards/{card_number_url_parse}-back.png') is True:
            back_art = request_swudb(f'https://swudb.com/images/cards/{card_number_url_parse}-back.png').content
        elif ping_swudb(f'https://swudb.com/images/cards/{card_number_url_parse}-portrait.png') is True:
            back_art = request_swudb(f'https://swudb.com/images/cards/{card_number_url_parse}-portrait.png').content
    else:
        title_query = '' if title == '' else f' title:"{title}"'
        json = request_swudb(f'https://swudb.com/api/search/{name}{title_query}?grouping=cards&sortorder=setno&sortdir=asc').json()
        art_url_suffix = sub('.+cards/', '', json.get('variants')[0].get('frontImagePath'))
        front_art = request_swudb(f'https://swudb.com/images/cards/{art_url_suffix}').content
        back_art = None
        if json.get('variants')[0].get('backImagePath') != '':
            art_url_suffix = sub('.+cards/', '', json.get('variants')[0].get('backImagePath'))
            back_art = request_swudb(f'https://swudb.com/images/cards/{art_url_suffix}').content
    
    for counter in range(quantity):
        if card_number == '':
            front_image_path = path.join(front_img_dir, f'{str(index)}{name}{'' if title == '' else f',{title}'}{str(counter + 1)}.png')
        else:
            front_image_path = path.join(front_img_dir, f'{str(index)}{card_number}{str(counter + 1)}.png')

        with open(front_image_path, 'wb') as f:
            f.write(front_art)

        if back_art != None:
            if card_number == '':
                back_image_path = path.join(back_img_dir, f'{str(index)}{name}{'' if title == '' else f',{title}'}{str(counter + 1)}.png')
            else:
                back_image_path = path.join(back_img_dir, f'{str(index)}{card_number}{str(counter + 1)}.png')

            with open(back_image_path, 'wb') as f:
                f.write(back_art)

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
    