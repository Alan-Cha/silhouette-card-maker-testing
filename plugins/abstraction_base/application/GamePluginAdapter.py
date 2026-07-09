from __future__ import annotations

from asyncio import gather, to_thread
from collections import OrderedDict

from plugins.abstraction_base.domain.Card import Card
from plugins.abstraction_base.domain.Deck import Deck
from plugins.abstraction_base.application.GamePluginPort import GamePluginLike

class GamePlugin(GamePluginLike[Card]):

    async def parse_deck(self, decklist: str):
        original_deck: Deck[Card] = await self.format.parse_decklist(decklist)

        filtered_deck: Deck[Card] = await self.deduplicate_deck(original_deck)

        deck_with_images: Deck[Card] = await self.get_card_images_for_deck(filtered_deck)

        return deck_with_images
    
    async def deduplicate_deck(self, deck: Deck[Card]):
        filtered_deck: OrderedDict[str, Card] = OrderedDict()

        for card in deck.cards:
            if card.id in filtered_deck:
                existing_card: Card = filtered_deck[card.id]
                existing_card.quantity += card.quantity
                existing_card.placements += card.placements
            else:
                filtered_deck[card.id] = card

        merged_deck: Deck[Card] = Deck(cards=list(filtered_deck.values()))
        return merged_deck
    
    async def get_card_images_for_deck(self, deck: Deck[Card]):
        cards_of_image_deck = []

        for card in deck.cards:
            image_card: Card = card
            image_card.front_image = await self.image_repository.get_image(card)
            cards_of_image_deck.append(card)

        return Deck(cards=cards_of_image_deck)
    
    async def save_deck(self, deck: Deck[Card]):
        await gather(
            *(to_thread(self.image_repository.save_image, card) for card in deck.cards)
        )

    async def run(self, decklist: str):

        deck: Deck[Card] = await self.parse_deck(decklist)

        await self.save_deck(deck)