from re import IGNORECASE, compile
from time import sleep
from typing import List, Tuple

import cloudscraper

# Master Vault sits behind Cloudflare, so use cloudscraper with its default browser fingerprint.
scraper = cloudscraper.create_scraper()

DECK_API_TEMPLATE = 'https://www.keyforgegame.com/api/decks/{deck_id}/?links=cards'

# Decks of KeyForge and Master Vault both key decks by the same UUID.
UUID_PATTERN = compile(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', IGNORECASE)

RATE_LIMIT_SECONDS = 0.075

card_count_tuple = Tuple[str, int] # card name, quantity

def request_mastervault(url: str):
    r = scraper.get(url, headers={'accept': 'application/json'})

    # Check for 2XX response code
    r.raise_for_status()

    sleep(RATE_LIMIT_SECONDS)

    return r

def extract_deck_id(url: str) -> str:
    match = UUID_PATTERN.search(url)
    if not match:
        raise Exception(f'could not find a deck ID in "{url}"')

    return match.group(0)

def get_deck_card_counts(deck_id: str) -> List[card_count_tuple]:
    data = request_mastervault(DECK_API_TEMPLATE.format(deck_id=deck_id)).json()

    linked_cards = data.get('_linked', {}).get('cards', [])
    cards_by_id = {card.get('id'): card for card in linked_cards if card.get('id') is not None}

    def card_name(card_id: str, card: dict) -> str:
        # Archon Arcana uses English card titles. Fall back to the card ID if
        # neither title field is present rather than raising, matching the
        # arkham_horror_lcg plugin's card.get('name') or code convention.
        return card.get('card_title_en') or card.get('card_title') or card_id

    # A dict preserves insertion order, so counts stay in the deck's card order.
    counts = {}

    def add_card(name: str) -> None:
        counts[name] = counts.get(name, 0) + 1

    # data._links.cards lists every card in the deck including non-deck cards such as Prophecies
    for card_id in data.get('data', {}).get('_links', {}).get('cards', []):
        card = cards_by_id.get(card_id)
        if card is not None:
            add_card(card_name(card_id, card))

    return list(counts.items())
