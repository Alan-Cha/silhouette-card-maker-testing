from __future__ import annotations

from re import compile
from json import dumps

from plugins.sorcery_contested_realm.domain.SorceryCard import SorceryCard
from plugins.abstraction_base.domain.Deck import Deck
from plugins.abstraction_base.infrastructure.DeckSearcherPort import DeckSearcherLike
from plugins.abstraction_base.infrastructure.WebRequest import perform_web_request, DEFAULT_WEB_HEADERS, PayloadType

class CuriosaDeckSearcher(DeckSearcherLike[SorceryCard]):

    URL_PATTERN = compile(r'https:\/\/curiosa.io\/decks\/(.+)')
    API_URL = 'https://curiosa.io/api/trpc/'
    DECK_ENDPOINTS = [
        'deck.getDecklistById',
        'deck.getAvatarById',
        'deck.getSideboardById',
        'deck.getMaybeboardById',
    ]
    CURIOSA_REFERER = 'https://curiosa.io/'

    async def is_url_for_deck(self, deck_url: str):
        return bool(self.URL_PATTERN.match(deck_url))
    
    async def get_cards(self, card_result):
        result = card_result.get('result', {}).get('data', {}).get('json', [])
        if isinstance(result, dict):
            return [result]
        return result
    
    async def extract_deck_from_url(self, deck_url: str):

        from plugins.sorcery_contested_realm.application.CuriosaDeckFormat import CuriosaDeckFormat
        
        extracted_deck: list[SorceryCard] = []

        curiosa_format = CuriosaDeckFormat()

        match = self.URL_PATTERN.match(deck_url)
        if match:
            deck_id = match.group(1).strip()
            api_url = self.API_URL + ','.join(self.DECK_ENDPOINTS)
            deck_payload = {str(i): {'json': {'id': deck_id}} for i in range(len(self.DECK_ENDPOINTS))}
            params = {'batch': '1', 'input': dumps(deck_payload)}
            headers = DEFAULT_WEB_HEADERS
            headers['referer'] = self.CURIOSA_REFERER
            api_response = await perform_web_request(api_url, request_headers=headers, request_payload_type=PayloadType.PARAMS, request_payload=params)

            if api_response is None:
                return extracted_deck

            unmapped_deck = []
            json_of_response = api_response.json()
            for result in json_of_response:
                cards_of_result = await self.get_cards(result)
                unmapped_deck += cards_of_result

            card_index = 0
            for card in unmapped_deck:
                card_index += 1

                extracted_card: SorceryCard = await curiosa_format.extract_card_data_from_card_line(card, card_index)

                extracted_deck.append(extracted_card)

        return Deck(cards=extracted_deck)