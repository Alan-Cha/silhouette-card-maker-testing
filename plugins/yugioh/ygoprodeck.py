import os
import requests
from time import sleep

session = requests.Session()

def request_api(query: str) -> requests.Response:
    r = session.get(query, headers = {'user-agent': 'silhouette-card-maker/0.1', 'accept': '*/*'})

    # Check for 2XX response code
    r.raise_for_status()

    sleep(0.075)

    return r

def fetch_card_art(passcode: int, quantity: int, front_img_dir: str):
    card_front_image_query = f'https://images.ygoprodeck.com/images/cards/{passcode}.jpg'
    card_art = request_api(card_front_image_query).content
    if card_art is not None:

        # Save image based on quantity
        for counter in range(quantity):
            image_path = os.path.join(front_img_dir, f'{passcode}_{counter + 1}.jpg')

            with open(image_path, 'wb') as f:
                f.write(card_art)

            print(f'{image_path}')