import enum
import time
from dataclasses import dataclass
from datetime import datetime
from io import BytesIO
from typing import Any, Callable, Iterable
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse
from uuid import UUID

import requests
from PIL import Image
from serde import field, serde
from serde.json import from_json

from plugins.mtg import remote
from plugins.mtg.common import MtgPrintedLanguage, partition

type _URI = str
type BytesPNG = bytes

type CardName = str
type SetCode = str
type CollectorNumber = str  # n.b. NOT a number. arbitrary string.


# Last updated: 2026-07-18
class BorderColour(enum.StrEnum):
    BLACK = enum.auto()
    WHITE = enum.auto()
    BORDERLESS = enum.auto()
    YELLOW = enum.auto()
    SILVER = enum.auto()
    GOLD = enum.auto()


# Last updated: 2026-07-18
class FrameEffect(enum.StrEnum):
    LEGENDARY = enum.auto()
    MIRACLE = enum.auto()
    ENCHANTMENT = enum.auto()
    DRAFT = enum.auto()
    DEVOID = enum.auto()
    TOMBSTONE = enum.auto()
    COLORSHIFTED = enum.auto()
    INVERTED = enum.auto()
    SUNMOONDFC = enum.auto()
    COMPASSLANDDFC = enum.auto()
    ORIGINPWDFC = enum.auto()
    MOONELDRAZIDFC = enum.auto()
    WAXINGANDWANINGMOONDFC = enum.auto()
    SHOWCASE = enum.auto()
    EXTENDEDART = enum.auto()
    COMPANION = enum.auto()
    ETCHED = enum.auto()
    SNOW = enum.auto()
    LESSON = enum.auto()
    SHATTEREDGLASS = enum.auto()
    CONVERTDFC = enum.auto()
    FANDFC = enum.auto()
    UPSIDEDOWNDFC = enum.auto()
    SPREE = enum.auto()


# Last updated: 2026-07-18
class ImageStatus(enum.StrEnum):
    MISSING = enum.auto()
    PLACEHOLDER = enum.auto()
    LOWRES = enum.auto()
    HIGHRES_SCAN = enum.auto()  # sic


# Last updated: 2026-07-18
class Language(enum.StrEnum):
    ENGLISH = "en"
    SPANISH = "es"
    FRENCH = "fr"
    GERMAN = "de"
    ITALIAN = "it"
    PORTUGUESE = "pt"
    JAPANESE = "ja"
    KOREAN = "ko"
    RUSSIAN = "ru"
    SIMPLIFIED_CHINESE = "zhs"
    TRADITIONAL_CHINESE = "zht"
    ANCIENT_GREEK = "grc"
    PHYREXIAN = "ph"

    @staticmethod
    def from_printed_lang(x: MtgPrintedLanguage) -> 'Language':
        match x:
            case MtgPrintedLanguage.ENGLISH:
                return Language.ENGLISH
            case MtgPrintedLanguage.SPANISH:
                return Language.SPANISH
            case MtgPrintedLanguage.FRENCH:
                return Language.FRENCH
            case MtgPrintedLanguage.GERMAN:
                return Language.GERMAN
            case MtgPrintedLanguage.ITALIAN:
                return Language.ITALIAN
            case MtgPrintedLanguage.PORTUGUESE:
                return Language.PORTUGUESE
            case MtgPrintedLanguage.JAPANESE:
                return Language.JAPANESE
            case MtgPrintedLanguage.KOREAN:
                return Language.KOREAN
            case MtgPrintedLanguage.RUSSIAN:
                return Language.RUSSIAN
            case MtgPrintedLanguage.SIMPLIFIED_CHINESE:
                return Language.SIMPLIFIED_CHINESE
            case MtgPrintedLanguage.TRADITIONAL_CHINESE:
                return Language.TRADITIONAL_CHINESE
            case MtgPrintedLanguage.ANCIENT_GREEK:
                return Language.ANCIENT_GREEK
            case MtgPrintedLanguage.PHYREXIAN:
                return Language.PHYREXIAN


# Last updated: 2026-07-18
# https://scryfall.com/docs/api/layouts
class Layout(enum.StrEnum):
    ADVENTURE = enum.auto()
    ART_SERIES = enum.auto()
    AUGMENT = enum.auto()
    BATTLE = enum.auto()
    CASE = enum.auto()
    CLASS = enum.auto()
    DOUBLE_FACED_TOKEN = enum.auto()
    EMBLEM = enum.auto()
    FLIP = enum.auto()
    HOST = enum.auto()
    LEVELER = enum.auto()
    MELD = enum.auto()
    MODAL_DFC = enum.auto()
    MUTATE = enum.auto()
    NORMAL = enum.auto()
    PLANAR = enum.auto()
    PREPARE = enum.auto()
    PROTOTYPE = enum.auto()
    REVERSIBLE_CARD = enum.auto()
    SAGA = enum.auto()
    SCHEME = enum.auto()
    SPLIT = enum.auto()
    TOKEN = enum.auto()
    TRANSFORM = enum.auto()
    VANGUARD = enum.auto()

    @property
    def double_sided(self) -> bool:
        match self:
            case self.ART_SERIES:
                return True
            case self.DOUBLE_FACED_TOKEN:
                return True
            case self.MELD:
                return True
            case self.MODAL_DFC:
                return True
            case self.REVERSIBLE_CARD:
                return True
            case self.TRANSFORM:
                return True
            case _:
                return False


# Last updated: 2026-07-18
# https://scryfall.com/docs/api/cards
class Rarity(enum.StrEnum):
    BONUS = enum.auto()
    COMMON = enum.auto()
    MYTHIC = enum.auto()
    RARE = enum.auto()
    SPECIAL = enum.auto()
    UNCOMMON = enum.auto()


# Last updated: 2026-07-18
# Subset of properties.
@serde
class Face:
    name: str
    image_uris: dict[str, _URI] = field(
        default_factory=dict
    )  # type not defined by spec
    layout: Layout | None = None  # defined IIF reversible
    object: str = 'card_face'  # must be `card_face`


# Last updated: 2026-07-18
@serde
class RelatedCardObject:
    class Component(enum.StrEnum):
        COMBO_PIECE = enum.auto()
        MELD_PART = enum.auto()
        MELD_RESULT = enum.auto()
        TOKEN = enum.auto()

    component: Component
    id: UUID
    name: str
    type_line: str
    uri: _URI
    object: str = 'related_card'  # must be `related_card`


# Last updated: 2026-07-18
# Subset of properties.
# https://scryfall.com/docs/api/cards
@serde
class Card:
    booster: bool
    collector_number: CollectorNumber  # not a number, despite the name
    digital: bool
    full_art: bool
    border_color: BorderColour
    id: UUID  # actually a UUID
    image_status: ImageStatus
    lang: Language
    layout: Layout
    name: CardName
    nonfoil: bool
    oversized: bool
    prints_search_uri: _URI
    promo: bool
    rarity: Rarity
    released_at: datetime
    reprint: bool
    rulings_uri: _URI
    scryfall_set_uri: _URI
    scryfall_uri: _URI
    set_id: UUID
    set_name: str
    set_type: str
    set_uri: _URI
    set: SetCode
    story_spotlight: bool
    textless: bool
    uri: _URI
    variation: bool  # implies `variation_of` TODO: enforce
    all_parts: list[RelatedCardObject] = field(default_factory=list)
    card_back_id: UUID | None = None  # SPEC ERROR: not always available
    card_faces: list[Face] = field(default_factory=list)
    frame_effects: list[FrameEffect] = field(default_factory=list)
    image_uris: dict[str, _URI] = field(
        default_factory=dict
    )  # type not defined by spec
    object: str = 'card'  # must be `card`
    oracle_id: UUID | None = None
    resource_id: str | None = None
    variation_of: UUID | None = None  # implies `variation = true` TODO: enforce

    # ASSUME: `id` is indeed a PK of the data
    def __hash__(self) -> int:
        return hash(self.id)


# API internal stuff. Incomplete, doesn't directly handle the error type variant.
@serde
class _SearchResponse:
    data: list[Card]


def _append_search_filter(uri: str, filter_term: str) -> str:
    parsed = urlparse(uri)
    params = parse_qs(parsed.query, keep_blank_values=True)
    q_val = params.get('q', [''])[0]
    params['q'] = [q_val + ' ' + filter_term]
    return urlunparse(parsed._replace(query=urlencode(params, doseq=True)))


def _fetch_printings(
    name: str, prints_search_uri: _URI, prefer_ub: bool | None
) -> list[Card]:
    xs: list[Card] = []
    if prefer_ub is not None:
        filter_term = 'is:ub' if prefer_ub else '-is:ub'
        filtered_uri = _append_search_filter(prints_search_uri, filter_term)

        try:
            xs = from_json(
                _SearchResponse, _request_scryfall(filtered_uri).content
            ).data
        except requests.exceptions.HTTPError:
            xs = []

        if not xs:
            label = 'No Universe Beyond' if prefer_ub else 'All'
            flag = '--prefer_ub' if prefer_ub else '--ignore_ub'
            print(
                f'{label} printings for "{name}" are Universe Beyond. Ignoring {flag}.'
            )

    if not xs:
        xs = from_json(
            _SearchResponse, _request_scryfall(prints_search_uri).content
        ).data

    return xs


@remote.memo
def _request_scryfall(
    query: str,
    params: dict[str, Any] | None = None,
) -> requests.Response:
    r = remote.get(query, params)

    # Apply rate limiting per Scryfall API documentation
    # See: https://scryfall.com/docs/api/rate-limits
    # Note: Direct image downloads from *.scryfall.io CDN have NO rate limits

    if "cards/search" in query or "cards/named" in query:
        time.sleep(0.5)  # Search/named endpoints: 2 requests/second (500ms delay)
    elif 'api.scryfall.com' in query:
        time.sleep(0.1)  # All other API methods: 10 requests/second (100ms delay)
    # else: No rate limiting needed for direct image downloads from *.scryfall.io CDN

    return r


def _fetch_meld_back(card: Card) -> BytesPNG | None:
    def parts(component: RelatedCardObject.Component):
        return [part for part in card.all_parts if part.component == component]

    meld_results = parts(RelatedCardObject.Component.MELD_RESULT)
    meld_parts = parts(RelatedCardObject.Component.MELD_PART)
    # FUTURE WORK: move this validation to post-validate on `Card`
    assert (
        len(meld_results) == 1
    ), "malformed meld card: does not have exactly 1 `meld_result`"
    assert (
        len(meld_parts) == 2
    ), "malformed meld card: does not have exactly 2 `meld_part`s"
    meld_result = meld_results[0]

    # Don't fetch back if this card is the meld result itself
    if meld_result.name == card.name:
        return None

    # Find the 0-based index of this card within meld_parts (the two non-result halves).
    # Scryfall lists meld parts in a consistent order; index 0 = top half, index 1 = bottom half.
    # next() returns the first index i where the part's name matches, or -1 as the default.
    meld_part_index = next(
        (i for i, p in enumerate(meld_parts) if p.name == card.name), -1
    )
    assert meld_part_index != -1, "malformed meld card: no meld parts w/ card's name"

    # Fetch the meld result card info; the PNG URL is in the response, no second request needed
    meld_result_json = from_json(Card, _request_scryfall(meld_result.uri).content)
    meld_result_image_data: bytes = _request_scryfall(
        meld_result_json.image_uris['png']
    ).content

    # Split the meld result image into top/bottom halves
    img = Image.open(BytesIO(meld_result_image_data))
    width, height = img.size
    half_height = height // 2

    # Scryfall lists meld parts by collector number; index 0 is the lower-numbered card,
    # which corresponds to the bottom half of the combined image.
    if meld_part_index == 0:
        cropped = img.crop((0, half_height, width, height))  # bottom half
    else:
        cropped = img.crop((0, 0, width, half_height))  # top half

    # Rotate 90° clockwise (meld result images are stored upright)
    cropped = cropped.rotate(-90, expand=True)

    # Resize to full card dimensions
    resized = cropped.resize((width, height), Image.LANCZOS)

    output = BytesIO()
    resized.save(output, format="png")
    return output.getvalue()


def _build_image_url(
    card_set: SetCode, card_collector_number: CollectorNumber, prefer_lang: Language
) -> str:
    if prefer_lang != Language.ENGLISH:
        return f'https://api.scryfall.com/cards/{card_set}/{card_collector_number}/{prefer_lang.value}?format=image&version=png'

    return f'https://api.scryfall.com/cards/{card_set}/{card_collector_number}/?format=image&version=png'


def _progressive_filtering(
    printings: Iterable[Card], filters: Iterable[Callable[[Card], bool]]
) -> list[Card]:
    pool = list(printings)
    leftovers: list[Card] = []

    for condition in filters:
        matched, not_matched = partition(pool, condition)
        leftovers = not_matched + leftovers
        pool = matched or pool  # Only narrow if we have any matches

    return pool + leftovers


def fetch_image(
    card_set: SetCode,
    collector_number: CollectorNumber,
    prefer_langs: list[Language],
    face: str | None = None,
) -> bytes | None:
    langs_to_try = list(prefer_langs)
    if not langs_to_try or langs_to_try[-1] != Language.ENGLISH:
        langs_to_try.append(Language.ENGLISH)

    last_error: Exception | None = None
    for lang in langs_to_try:
        url = _build_image_url(card_set, collector_number, lang)
        if face:
            url = f'{url}&face={face}'

        try:
            return _request_scryfall(url).content
        except requests.exceptions.HTTPError as e:
            if e.response is None or e.response.status_code != 404:
                raise

            last_error = e
            print(
                f'Language "{lang.value}" not available for set code: {card_set} and collector number: {collector_number}.'
            )

    assert last_error is not None
    raise last_error


def _fetch_face(card: Card, *, face: str | None = None) -> BytesPNG:
    url = _build_image_url(card.set, card.collector_number, card.lang)
    if face:
        url = f'{url}&face={face}'
    return _request_scryfall(url).content


@dataclass(frozen=True)
class CardFaces:
    front: BytesPNG
    back: BytesPNG | None = None  # not all cards are double sided


def fetch_faces(
    card: Card,
) -> CardFaces:
    if card.layout == Layout.MELD:  # meld is double-sided but has a weird layout.
        back = _fetch_meld_back(card)
    elif card.layout.double_sided:  # non-meld double-sided are simple to handle
        back = _fetch_face(card, face='back')
    else:
        back = None

    return CardFaces(front=_fetch_face(card), back=back)


def tokens(card: Card) -> list[Card]:
    return [
        from_json(Card, _request_scryfall(r.uri).content)
        for r in card.all_parts
        if r.component == RelatedCardObject.Component.TOKEN
    ]


def fetch_card(
    name: CardName,
    set_code: SetCode | None = None,
    collector_number: CollectorNumber | None = None,
    *,
    ignore_set_and_collector_number: bool = False,
    ignore_sets: set[str] = set(),
    ignore_ub: bool = False,
    prefer_extra_art: bool = False,
    prefer_langs: list[Language] = [],
    prefer_older_sets: bool = False,
    prefer_sets: list[str] = [],
    prefer_showcase: bool = False,
    prefer_ub: bool = False,
) -> Card:
    if name == "":
        raise ValueError("card name cannot be empty")

    # Define filters in order of preference.
    # Language filters are applied FIRST to ensure we only consider printings available in the preferred language.
    # This prevents situations where full-art/showcase versions are selected but only available in English.
    # prefer_langs is an ordered list: each language gets its own filter so earlier languages rank higher.
    # prefer_sets is an ordered list: each set gets its own filter so earlier sets rank higher.
    prefer_filters: list[Callable[[Card], bool]] = [
        *[(lambda c, lang=lang: c.lang == lang) for lang in prefer_langs],
        lambda c: c.nonfoil,
        lambda c: not c.digital,
        lambda c: not c.promo,
        *[(lambda c, s=s: c.set == s) for s in prefer_sets],
        lambda c: not prefer_showcase ^ (FrameEffect.SHOWCASE in c.frame_effects),
        lambda c: not prefer_extra_art
        ^ (
            c.full_art
            or c.border_color == "borderless"
            or FrameEffect.EXTENDEDART in c.frame_effects
        ),
    ]

    # Query based on card set and card collector number if provided
    if (
        not ignore_set_and_collector_number
        and set_code is not None
        and collector_number is not None
    ):
        return from_json(
            Card,
            _request_scryfall(
                f"https://api.scryfall.com/cards/{set_code.lower()}/{collector_number}"
            ).content,
        )

    # Don't have (or don't want to use) set/collector-id to pick exact card.
    # Look for the best match instead.

    # Start by name.
    try:
        card = from_json(
            Card,
            _request_scryfall(
                'https://api.scryfall.com/cards/named', params={'exact': name}
            ).content,
        )
    except requests.exceptions.HTTPError as e:
        if e.response is None or e.response.status_code != 404:
            raise  # something went wrong with the query

        # Fall back to flavor name search (e.g. Godzilla series, convention promos)
        search = from_json(
            _SearchResponse,
            _request_scryfall(
                'https://api.scryfall.com/cards/search',
                params={'q': f'flavor_name:"{name}"', 'unique': 'cards'},
            ).content,
        )
        if not search.data:
            raise  # flavour name search gave nothing, re-raise original error

        card = search.data[0]

    # If we've filters, then look through all printings for the best variant.
    needs_filtering = (
        prefer_langs
        or prefer_older_sets
        or prefer_sets
        or ignore_sets
        or prefer_showcase
        or prefer_extra_art
        or prefer_ub
        or ignore_ub
    )
    if needs_filtering:
        ub_preference = True if prefer_ub else (False if ignore_ub else None)
        printings = _fetch_printings(name, card.prints_search_uri, ub_preference)
        assert printings  # ?? found one card instance, but no printings?

        remaining = [c for c in printings if c.set not in ignore_sets]
        if remaining:
            printings = remaining
        else:
            print(
                f'All printings for "{name}" are in ignored sets. Ignoring --ignore_set.'
            )

        # ASSUME: `card_printings` sorted by age, newest first
        if prefer_older_sets:
            printings.reverse()

        filtered = _progressive_filtering(printings, prefer_filters)
        if filtered:
            card = filtered[0]
        else:
            print(
                f'No printings found for "{name}" with preferred options. Using default instead.'
            )

    return card
