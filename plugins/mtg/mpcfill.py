import os
from base64 import b64decode
from typing import List, Set, Tuple

import requests
from filetype.filetype import guess_extension

def request_mpcfill(card_id: str) -> requests.Response:
    base_url = "https://script.google.com/macros/s/AKfycbw8laScKBfxda2Wb0g63gkYDBdy8NWNxINoC4xDOwnCQ3JMFdruam1MdmNmN4wI5k4/exec?id="
    r = requests.get(base_url + card_id, headers = {"user-agent": "silhouette-card-maker/0.1", "accept": "*/*"})

    r.raise_for_status()

    return r

def fetch_card(
        index: int, 
        quantity: int, 
        
        card_id: str,
        clean_card_name: str,
        back_card_id: str | None,

        front_img_dir: str,
        double_sided_dir: str,

) -> None:
    card_art = request_mpcfill(card_id).content

    if card_art is not None:
        card_art = b64decode(card_art)
        card_art_ext = guess_extension(card_art)
        for counter in range(quantity):
            image_path = os.path.join(front_img_dir, f'{str(index)}{clean_card_name}{str(counter + 1)}.{card_art_ext}')

            with open(image_path, 'wb') as f:
                f.write(card_art)
    
    if back_card_id:
        card_art = request_mpcfill(back_card_id).content

        if card_art is not None:
            card_art = b64decode(card_art)
            card_art_ext = guess_extension(card_art)
            for counter in range(quantity):
                image_path = os.path.join(double_sided_dir, f'{str(index)}{clean_card_name}{str(counter + 1)}.{card_art_ext}')

                with open(image_path, 'wb') as f:
                    f.write(card_art)

def get_handle_card(
    front_img_dir: str,
    double_sided_dir: str
):
    def configured_fetch_card(index: int, card_id, name: str, back_card_id: str | None, quantity: int = 1):
        fetch_card(
            index,
            quantity,

            card_id,
            name,
            back_card_id,

            front_img_dir,
            double_sided_dir,

        )
    return configured_fetch_card