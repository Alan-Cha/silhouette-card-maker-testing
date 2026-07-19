import functools
import os
import sys
from collections import OrderedDict
from pathlib import Path
from typing import Iterable
from uuid import UUID

import click

# Add parent directory to path to allow imports when run as a script
REPO_ROOT = Path(__file__).parent.parent.parent.absolute()
sys.path.insert(0, str(REPO_ROOT))


from plugins.mtg import remote, scryfall
from plugins.mtg.common import MtgPrintedLanguage, partition, remove_nonalphanumeric
from plugins.mtg.deck_formats import (
    DeckFormat,
    FetchCard,
    parse_deck,
    unparse,
)
from plugins.mtg.mpcfill import get_handle_card as mpc_get_handle_card
from plugins.mtg.mpcfill import prefetch_mpcfill
from plugins.mtg.scryfall import Card, CardName
from utilities import ensure_directory

# CONSTANTS
FRONT_DIR = REPO_ROOT / 'game' / 'front'
DOUBLE_SIDED_DIR = REPO_ROOT / 'game' / 'double_sided'


# Pairs single-faced cards together. Intended for grouping single-face tokens.
# PRECONDITION: `forall x \in cards. x is single-faced`
# FIXME: O(n^2)
def _generate_paired_faces(
    cards: Iterable[tuple[Card, int]],
) -> list[tuple[CardName, scryfall.CardFaces]]:
    card_queue: list[tuple[Card, scryfall.BytesPNG]] = []
    for card, quantity in cards:
        print(f"fetching image: {card.name} ({card.set}) {card.collector_number}")
        faces = scryfall.fetch_faces(card)
        assert (
            faces.back is None
        ), "PRECONDITION: single face tokens shouldn't have a back"
        card_queue += [(card, faces.front)] * quantity

    # process in reverse for cheap(er) pop
    card_queue.reverse()
    paired_with = set[UUID]()

    def pick_pairing() -> tuple[Card, scryfall.BytesPNG] | None:
        for i in range(1, len(card_queue)+1):
            card, _ = card_queue[-i]
            if card.id not in paired_with:
                return card_queue.pop(-i)

        return None

    prev_front_card_id: UUID | None = None

    def reset_pairings(front_card: Card):
        nonlocal prev_front_card_id
        prev_front_card_id = front_card.id
        paired_with.clear()
        # never pair with ourselves. prefer to have it blank.
        paired_with.add(front_card.id)

    deck_raw: list[tuple[CardName, scryfall.CardFaces]] = []
    while card_queue:
        front_card, front_face = card_queue.pop()
        back_face: scryfall.BytesPNG | None = None

        if prev_front_card_id is None or prev_front_card_id != front_card.id:
            reset_pairings(front_card)

        if (pair := pick_pairing()) is None:
            # clear candidates & try again, but never pair with self
            reset_pairings(front_card)
            pair = pick_pairing()

        if pair is not None:
            back_card, back_face = pair
            paired_with.add(back_card.id)
            print(f"pairing tokens: `{front_card.name}` w/ `{back_card.name}`")
        else:
            print(f'NOTE: unpaired token `{front_card.name}`. maybe add another token?')

        deck_raw.append(
            (front_card.name, scryfall.CardFaces(front=front_face, back=back_face))
        )

    return deck_raw


# n.b. `CardName` can be a partial lie due to token face pairing feature.
def _generate_deck_faces(
    deck: OrderedDict[Card, int],
) -> list[tuple[CardName, scryfall.CardFaces]]:
    boring, tokens = partition(
        deck.items(), lambda kv: kv[0].layout != scryfall.Layout.TOKEN
    )
    deck_raw: list[tuple[CardName, scryfall.CardFaces]] = []

    for card, quantity in boring:
        print(f"fetching image: {card.name} ({card.set}) {card.collector_number}")
        faces = scryfall.fetch_faces(card)
        deck_raw += [(card.name, faces)] * quantity

    deck_raw += _generate_paired_faces(tokens)
    return deck_raw


def report_tokens(format: DeckFormat, cards: Iterable[Card]):
    tokens = OrderedDict[Card, int]()

    for card in cards:
        for token in scryfall.tokens(card):
            tokens.setdefault(token, 0)
            tokens[token] += 1

    for token, quantity in tokens.items():
        print(unparse(format, token, quantity))


def generate_deck(deck: OrderedDict[Card, int]):
    card_faces = _generate_deck_faces(deck)
    for i, (name, faces) in enumerate(card_faces):
        # FUTURE WORK: other img types?
        def save_face(dir: Path, face: scryfall.BytesPNG | None):
            if face is not None:
                with open(dir / f'{i}_{remove_nonalphanumeric(name)}.png', 'wb') as f:
                    f.write(face)

        save_face(FRONT_DIR, faces.front)
        save_face(DOUBLE_SIDED_DIR, faces.back)


# fmt: off
@click.command()
@click.argument('deck_path')
@click.argument('deck_format', type=click.Choice([t.value for t in DeckFormat], case_sensitive=False))
@click.option('-i', '--ignore_set_and_collector_number', default=False, is_flag=True, show_default=True, help="Ignore provided sets and collector numbers when fetching cards.")
@click.option('--prefer_older_sets', default=False, is_flag=True, show_default=True, help="Prefer fetching cards from older sets if sets are not provided.")
@click.option('-s', '--prefer_set', multiple=True, help="Prefer fetching cards from a particular set(s) if sets are not provided. Use this option multiple times to specify multiple preferred sets.")
@click.option('--ignore_set', multiple=True, help="Exclude a set from consideration when fetching cards. Use this option multiple times to exclude multiple sets.")
@click.option('--prefer_showcase', default=False, is_flag=True, show_default=True, help="Prefer fetching cards with showcase treatment")
@click.option('--prefer_extra_art', default=False, is_flag=True, show_default=True, help="Prefer fetching cards with full art, borderless, or extended art.")
@click.option('--prefer_lang', multiple=True, type=click.Choice([lang.value for lang in MtgPrintedLanguage], case_sensitive=False), help="Preferred language for card images (printed code). Use multiple times for a priority list. Falls back to English if none are available.")
@click.option('--prefer_ub', default=False, is_flag=True, show_default=True, help="Prefer Universe Beyond printings when available.")
@click.option('--ignore_ub', default=False, is_flag=True, show_default=True, help="Exclude Universe Beyond printings from consideration.")
@click.option('--tokens', default=False, is_flag=True, show_default=True, help="Fetch related tokens when fetching cards")
# fmt: on


def cli(
    deck_path: str,
    deck_format: DeckFormat,
    *,
    ignore_set_and_collector_number: bool,
    ignore_set: Iterable[str],
    ignore_ub: bool,
    prefer_extra_art: bool,
    prefer_lang: Iterable[str],
    prefer_older_sets: bool,
    prefer_set: Iterable[str],
    prefer_showcase: bool,
    prefer_ub: bool,
    tokens: bool,
):
    ensure_directory(FRONT_DIR)
    ensure_directory(DOUBLE_SIDED_DIR)

    if deck_format == DeckFormat.URL:
        deck_text = deck_path
    else:
        if not os.path.isfile(deck_path):
            print(f'{deck_path} is not a valid file.')
            return

        with open(deck_path, 'r') as deck_file:
            deck_text = deck_file.read()

    if deck_format == DeckFormat.MPCFILL_XML:
        assert False, "MPCFill XML not supported"
        # get_handle_card = mpc_get_handle_card(
        #     front_directory,
        #     double_sided_directory
        # )
        # prefetch_mpcfill(extract_mpcfill_card_ids(deck_text))
    else:
        fetch: FetchCard = functools.partial(
            scryfall.fetch_card,
            ignore_set_and_collector_number=ignore_set_and_collector_number,
            ignore_sets=set(ignore_set),
            ignore_ub=ignore_ub,
            prefer_extra_art=prefer_extra_art,
            prefer_langs=[
                scryfall.Language.from_printed_lang(MtgPrintedLanguage(lang))
                for lang in prefer_lang
            ],
            prefer_older_sets=prefer_older_sets,
            prefer_sets=list(prefer_set),
            prefer_showcase=prefer_showcase,
            prefer_ub=prefer_ub,
        )

    errors, deck = parse_deck(
        deck_text,
        deck_format,
        fetch,
    )
    if errors:
        print('Errors occurred.')
        for src, err in errors:
            print(f"{src}\n: {err}")

        raise click.Abort()  # if there were errors, stop.

    if tokens:
        report_tokens(deck_format, deck.keys())
    else:
        generate_deck(deck)


if __name__ == '__main__':
    try:
        cli()
    finally:
        remote.cache_trim()
