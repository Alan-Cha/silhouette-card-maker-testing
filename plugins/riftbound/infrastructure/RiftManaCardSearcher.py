from re import sub, findall
from typing import Optional
from urllib.parse import urlencode, quote

from plugins.riftbound.domain.RiftboundCard import RiftboundCard
from plugins.abstraction_base.infrastructure.WebRequest import perform_web_request

RIFTMANA_CARD_API_TEMPLATE = 'https://riftmana.com/wp-json/card-list/v1/filter?{SEARCH_PARAMS}'
DEFAULT_SEARCH_PARAMS = {
    'search': 'CARD_NAME',
    'sort': 'id',
    'sort_dir': 'asc',
    'page': 1,
}

class RiftManaCardSeacher():
    async def get_card_number(self, card: RiftboundCard) -> Optional[str]:
        
        # Get the internal information based on the card name to route to the card itself
        sanitized = sub(r'[^A-Za-z0-9 \-]+', '', card.name)

        search_params = DEFAULT_SEARCH_PARAMS
        search_params['search'] = sanitized
        encoded_params = urlencode(search_params, quote_via=quote)

        url = RIFTMANA_CARD_API_TEMPLATE.format(SEARCH_PARAMS=encoded_params)

        name_response = await perform_web_request(url)

        if name_response is not None:
            # Now we can retrieve the card number
            cards_of_response = name_response.json().get('cards', '')
            match = findall(r'data-card-id=\\"([^"]+)\\"', cards_of_response)

            if match:
                return match.group(1)