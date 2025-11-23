from enum import Enum
from _collections_abc import Set
from typing import Callable, Tuple
from elestrals import DECK_ID_URL_TEMPLATE, request_elestrals

# card_data_tuple = Tuple[str, str, int] # name, image, quantity

# def parse_deck_helper(
#         deck_text: str,
#         handle_card: Callable,
#         is_card_line: Callable,
#         extract_card_data: Callable,
#     ) -> None:
#     error_lines = []

#     index = 0
#     for line in deck_text.strip().split('\n'):
#         if is_card_line(line):
#             index = index + 1

#             name, image, quantity = extract_card_data(line)

#             print(f'Index: {index}, quantity: {quantity}, name: {name}')
#             try:
#                 handle_card(index, name, image, quantity)
#             except Exception as e:
#                 print(f'Error: {e}')
#                 error_lines.append((line, e))
#         else:
#             print(f'Skipping: "{line}"')

#     if len(error_lines) > 0:
#         print(f'Errors: {error_lines}')

def parse_elestrals(deck_text: str, handle_card: Callable):
    deck_response = request_elestrals(DECK_ID_URL_TEMPLATE.format(deck_id=deck_text))

    data = deck_response.json().get("data")

    # Build a lookup for card data
    cards_data = {}
    for card in data.get("cards"):
        cards_data[card.get("_id")] = {
            "Name": card.get("name"),

            # large images don't exist for Elestrals, use small
            "Image": card.get("images").get("small")
        }

    index = 0
    for section in data.get("deck").get("sections"):
        for card in section.get("cards"):
            index += 1

            card_id = card.get("cardId")
            quantity = card.get("count")
            
            card_data = cards_data[card_id]
            name = card_data.get("Name")
            image = card_data.get("Image")

            print(f'Index: {index}, quantity: {quantity}, name: {name}')
            handle_card(index + 1, name, image, quantity)

class DeckFormat(str, Enum):
    ELESTRALS_PLAY_NETWORK = 'elestrals'

def parse_deck(deck_text: str, format: DeckFormat, handle_card: Callable):
    if format == DeckFormat.ELESTRALS_PLAY_NETWORK:
        parse_elestrals(deck_text, handle_card)
    else:
        raise ValueError('Unrecognized deck format.')
