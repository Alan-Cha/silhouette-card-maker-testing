"""
Tests for the MTG plugin.
Tests deck format parsing and image fetching from Scryfall.
"""

import copy
import shutil
import tempfile
import uuid
from io import BytesIO
from collections import OrderedDict
from datetime import datetime
from typing import Any, Callable
from unittest.mock import MagicMock, patch

import pytest
import requests
from serde.json import from_json, to_json

from plugins.mtg import scryfall
from plugins.mtg.common import MtgPrintedLanguage
from plugins.mtg.deck_formats import (
    DeckEntry,
    DeckFormat,
    DeckParse,
    FetchCard,
    parse_archidekt,
    parse_deck,
    parse_deckstats,
    parse_moxfield,
    parse_mtga,
    parse_mtgo,
    parse_scryfall_json,
    parse_simple_list,
)
from plugins.mtg.patterns import DECKSTATS_PATTERN, MOXFIELD_PATTERN
from plugins.mtg.scryfall import (
    Card,
    CardName,
    CollectorNumber,
    SetCode,
    _build_image_url,
    _fetch_printings,
    _request_scryfall,
)

# --- Unit Tests for Deck Format Parsing ---


def _dummy_fetch_card(
    name: CardName, set_code: SetCode | None, collector_number: CollectorNumber | None
) -> Card:
    return _mk_card(name, set_code or '', collector_number or '')


def _verify_deckparse(
    errs: list[tuple[str, Exception]],
    deck: OrderedDict[Card, int],
    expected_cards: list[DeckEntry],
):
    assert not errs
    assert len(expected_cards) == len(deck)
    for (name, card_set, collector_number, expected_quantity), (card, quantity) in zip(
        expected_cards, deck.items()
    ):
        assert name == card.name
        assert card_set == card.set
        assert collector_number == card.collector_number
        assert expected_quantity == quantity


def _verify_deck_parser(
    deck_parser: Callable[[str, FetchCard], DeckParse],
    deck_text: str,
    expected_cards: list[DeckEntry],
):
    errs, deck = deck_parser(deck_text, _dummy_fetch_card)
    _verify_deckparse(errs, deck, expected_cards)


class TestDeckFormatParsing:
    """Test regex pattern matching for special deck format cases."""

    def test_star_symbol_in_collector_number(self):
        """Test that Moxfield star symbol in collector numbers is matched."""
        # Moxfield exports can include ★ in collector numbers for special versions
        line = "1 Sol Ring (SLD) 123★"
        match = MOXFIELD_PATTERN.match(line)

        assert match is not None
        assert match.group(1) == "1"
        assert match.group(2) == "Sol Ring"
        assert match.group(3) == "SLD"
        assert match.group(4) == "123★"

    def test_collector_number_with_dash(self):
        """Test that collector numbers with dashes are matched."""
        # Collector numbers like "123-456" should also be captured
        line = "1 Some Card (SET) 123-456"
        match = MOXFIELD_PATTERN.match(line)

        assert match is not None
        assert match.group(4) == "123-456"

    def test_quantity_with_x(self):
        """Test that quantities with "x" suffix are matched."""
        # Moxfield format can include "x" after quantity (e.g. "4x")
        line = "4x Lightning Bolt (2XM) 117"
        match = MOXFIELD_PATTERN.match(line)

        assert match is not None
        assert match.group(1) == "4"
        assert match.group(2) == "Lightning Bolt"
        assert match.group(3) == "2XM"
        assert match.group(4) == "117"

    def test_deckstats_star_symbol_in_collector_number(self):
        """Test that Deckstats star symbol in collector numbers is matched."""
        # Deckstats can include ★ in collector numbers
        # e.g. "1 [SLD#1494★] Sol Ring"
        line = "1 [SLD#1494★] Sol Ring"
        match = DECKSTATS_PATTERN.match(line)

        assert match is not None
        assert match.group(1) == "1"
        assert match.group(2) == "SLD"
        assert match.group(3) == "1494★"
        assert match.group(4) == "Sol Ring"


class TestSimpleFormat:
    """Test the simple card name list format."""

    def test_parse_simple_list(self):
        """Test parsing a simple list of card names."""
        deck_text = """
Isshin, Two Heavens as One
Arid Mesa
Battlefield Forge
"""

        _verify_deck_parser(
            parse_simple_list,
            deck_text,
            [
                ("Isshin, Two Heavens as One", '', '', 1),
                ("Arid Mesa", '', '', 1),
                ("Battlefield Forge", '', '', 1),
            ],
        )


class TestMTGAFormat:
    """Test MTG Arena format parsing."""

    def test_parse_mtga_with_set_info(self):
        """Test parsing MTGA format with set and collector number."""
        deck_text = """
Deck
2 Arid Mesa (MH2) 244
1 Lion Sash (NEO) 26
"""

        _verify_deck_parser(
            parse_mtga,
            deck_text,
            [
                ("Arid Mesa", "MH2", '244', 2),
                ("Lion Sash", "NEO", '26', 1),
            ],
        )

    def test_parse_mtga_without_set_info(self):
        """Test parsing MTGA format without set information."""
        deck_text = """Deck
2x Mountain
1 Lightning Bolt"""

        _verify_deck_parser(
            parse_mtga,
            deck_text,
            [
                ("Mountain", '', '', 2),
                ("Lightning Bolt", '', '', 1),
            ],
        )


class TestMTGOFormat:
    """Test MTG Online format parsing."""

    def test_parse_mtgo(self):
        """Test parsing MTGO format."""
        deck_text = """
1 Ainok Bond-Kin
2 Witch Enchanter

SIDEBOARD:
1 Containment Priest
"""

        _verify_deck_parser(
            parse_mtgo,
            deck_text,
            [
                ("Ainok Bond-Kin", '', '', 1),
                ("Witch Enchanter", '', '', 2),
                ("Containment Priest", '', '', 1),
            ],
        )


class TestArchidektFormat:
    """Test Archidekt format parsing."""

    def test_parse_archidekt(self):
        """Test parsing Archidekt format with tags and foil markers."""
        deck_text = """
10x Agadeem's Awakening // Agadeem, the Undercrypt (znr) 90 [Resilience,Land]
2x Ashnod's Altar (ema) 218 *F* [Mana Advantage]
"""

        _verify_deck_parser(
            parse_archidekt,
            deck_text,
            [
                ("Agadeem's Awakening // Agadeem, the Undercrypt", 'znr', '90', 10),
                ("Ashnod's Altar", "ema", '218', 2),
            ],
        )


class TestDeckstatsFormat:
    """Test Deckstats format parsing."""

    def test_parse_deckstats_with_set(self):
        """Test parsing Deckstats format with set info."""
        deck_text = """//Main
131 [2XM#310] Ash Barrens
17 Blinkmoth Nexus
"""

        _verify_deck_parser(
            parse_deckstats,
            deck_text,
            [
                ("Ash Barrens", "2XM", '310', 131),
                ("Blinkmoth Nexus", '', '', 17),
            ],
        )

    def test_strips_commander_annotation(self):
        """Test that #!Commander annotation is stripped from card names."""
        deck_text = """
1 Varragoth, Bloodsky Sire #!Commander
1 Varragoth, Bloodsky Sire #!Commander
"""

        _verify_deck_parser(
            parse_deckstats,
            deck_text,
            [
                ("Varragoth, Bloodsky Sire", '', '', 2),
            ],
        )


class TestMoxfieldFormat:
    """Test Moxfield format parsing."""

    def test_parse_moxfield(self):
        """Test parsing Moxfield format."""
        deck_text = """
1 Ainok Bond-Kin (2X2) 5
2 Witch Enchanter // Witch-Blessed Meadow (MH3) 239
"""

        _verify_deck_parser(
            parse_moxfield,
            deck_text,
            [
                ("Ainok Bond-Kin", "2X2", '5', 1),
                ("Witch Enchanter // Witch-Blessed Meadow", 'MH3', '239', 2),
            ],
        )


class TestScryfallJsonFormat:
    """Test Scryfall JSON format parsing."""

    def test_parse_scryfall_json(self):
        """When image_uris.back is present, both front and back images are fetched."""
        card = _mk_card("Delver of Secrets", "isd", "51")

        def fetcher(
            name: CardName,
            card_set: SetCode | None,
            collector_number: CollectorNumber | None,
        ):
            assert name == card.name
            assert card_set == card.set
            assert collector_number == card.collector_number
            return card

        deck_text = to_json(
            {"entries": {"mainboard": [{"count": 1, "card_digest": card}]}}
        )

        errors, deck = parse_scryfall_json(deck_text, fetcher)
        assert errors == []
        assert len(deck) == 1
        deck_card, quantity = list(deck.items())[0]
        assert quantity == 1
        assert deck_card == card


# --- Unit Tests for Scryfall Fetching ---

_PRINTS_SEARCH_URI = (
    'https://api.scryfall.com/cards/search?q=oracleid%3Atest&unique=prints'
)


def _mk_card(
    name: CardName, set: SetCode, collector_number: CollectorNumber, **kw: Any
) -> Card:
    def mk_uuid(x: Any):
        return uuid.UUID(bytes=abs(hash(x)).to_bytes(length=16))

    kw.setdefault('booster', False)
    kw.setdefault('digital', False)
    kw.setdefault('full_art', False)
    kw.setdefault('border_color', scryfall.BorderColour.BLACK)
    kw.setdefault('id', mk_uuid(name))
    kw.setdefault('image_status', scryfall.ImageStatus.LOWRES)
    kw.setdefault('lang', scryfall.Language.ENGLISH)
    kw.setdefault('layout', scryfall.Layout.NORMAL)
    kw.setdefault('nonfoil', True)
    kw.setdefault('oversized', False)
    kw.setdefault('prints_search_uri', _PRINTS_SEARCH_URI)
    kw.setdefault('promo', False)
    kw.setdefault('rarity', scryfall.Rarity.COMMON)
    kw.setdefault('released_at', datetime.fromtimestamp(0))
    kw.setdefault('reprint', False)
    kw.setdefault('rulings_uri', "rulings-uri")
    kw.setdefault('scryfall_set_uri', "scryfall-set-uri")
    kw.setdefault('scryfall_uri', "dummy-URI")
    kw.setdefault('set_id', mk_uuid(set))
    kw.setdefault('set_name', "set-name-stub")
    kw.setdefault('set_type', "set-type-stub")
    kw.setdefault('set_uri', "set-uri")
    kw.setdefault('story_spotlight', False)
    kw.setdefault('textless', False)
    kw.setdefault('uri', "card-uri")
    kw.setdefault('variation', False)
    return Card(
        name=name,
        set=set,
        collector_number=collector_number,
        **kw,
    )


SHADOWSPEAR = _mk_card('Shadowspear', 'pza', '17')

# Skrelv has both a Universe Beyond printing (SLD) and a standard printing (ONE).
SKRELV_NON_UB_PRINTING = _mk_card('Skrelv, Defector Mite', 'one', '255')
SKRELV_UB_PRINTING = _mk_card('Skrelv, Defector Mite', 'sld', '1926')

# Excalibur only exists as a Universe Beyond card.
EXCALIBUR = _mk_card('Excalibur, Sword of Eden', 'acr', '72')


def _make_404():
    err = requests.exceptions.HTTPError()
    err.response = MagicMock()
    err.response.status_code = 404
    return err


def _named_response(card: Card):
    r = MagicMock()
    r.content = to_json(card)
    return r


def _printings_response(printings: list[Card]):
    r = MagicMock()
    r.content = to_json({'data': printings})
    return r


class TestFetchPrintingsUB:
    """Unit tests for Universe Beyond filtering in fetch_printings."""

    @patch('plugins.mtg.scryfall._request_scryfall')
    def test_prefer_ub_returns_ub_printings_when_available(self, mock_request):
        """prefer_ub=True fetches with is:ub filter and returns those results."""
        mock_request.return_value = _printings_response([SKRELV_UB_PRINTING])

        result = _fetch_printings('Skrelv, Defector Mite', _PRINTS_SEARCH_URI, True)

        assert result == [SKRELV_UB_PRINTING]
        called_url = mock_request.call_args_list[0][0][0]
        assert 'is%3Aub' in called_url or 'is:ub' in called_url

    @patch('plugins.mtg.scryfall._request_scryfall')
    def test_ignore_ub_returns_non_ub_printings_when_available(self, mock_request):
        """ignore_ub=True fetches with -is:ub filter and returns those results."""
        mock_request.return_value = _printings_response([SKRELV_NON_UB_PRINTING])

        result = _fetch_printings('Skrelv, Defector Mite', _PRINTS_SEARCH_URI, False)

        assert result == [SKRELV_NON_UB_PRINTING]
        called_url = mock_request.call_args_list[0][0][0]
        assert '-is%3Aub' in called_url or '-is:ub' in called_url

    @patch('plugins.mtg.scryfall._request_scryfall')
    def test_prefer_ub_falls_back_when_no_ub_printings(self, mock_request):
        """prefer_ub=True falls back to all printings when no UB printings exist."""
        mock_request.side_effect = [
            _printings_response([]),
            _printings_response([EXCALIBUR]),
        ]

        result = _fetch_printings('Excalibur, Sword of Eden', _PRINTS_SEARCH_URI, True)

        assert result == [EXCALIBUR]
        assert mock_request.call_count == 2

    @patch('plugins.mtg.scryfall._request_scryfall')
    def test_ignore_ub_falls_back_when_all_printings_are_ub(self, mock_request):
        """ignore_ub=True falls back to all printings when no non-UB printings exist."""
        mock_request.side_effect = [
            _printings_response([]),
            _printings_response([EXCALIBUR]),
        ]

        result = _fetch_printings('Excalibur, Sword of Eden', _PRINTS_SEARCH_URI, False)

        assert result == [EXCALIBUR]
        assert mock_request.call_count == 2

    @patch('plugins.mtg.scryfall._request_scryfall')
    def test_no_ub_filter_fetches_all_printings(self, mock_request):
        """prefer_ub=None skips the filtered request entirely."""
        mock_request.return_value = _printings_response(
            [SKRELV_UB_PRINTING, SKRELV_NON_UB_PRINTING]
        )

        result = _fetch_printings('Skrelv, Defector Mite', _PRINTS_SEARCH_URI, None)

        assert result == [SKRELV_UB_PRINTING, SKRELV_NON_UB_PRINTING]
        assert mock_request.call_count == 1
        assert mock_request.call_args_list[0][0][0] == _PRINTS_SEARCH_URI


class TestFetchCardUB:
    """Unit tests for prefer_ub/ignore_ub integration inside fetch_card."""

    @patch('plugins.mtg.scryfall._request_scryfall')
    def test_prefer_ub_selects_ub_printing(self, mock_request):
        """With prefer_ub=True, the UB printing is selected over the standard one."""
        mock_request.side_effect = [
            _named_response(SKRELV_NON_UB_PRINTING),  # /cards/named
            _printings_response([SKRELV_UB_PRINTING]),  # is:ub filtered search
        ]

        card = scryfall.fetch_card(
            name="Skrelv, Defector Mite",
            prefer_ub=True,
        )

        assert card.set == 'sld'
        assert card.collector_number == '1926'

    @patch('plugins.mtg.scryfall._request_scryfall')
    def test_ignore_ub_selects_non_ub_printing(self, mock_request):
        """With ignore_ub=True, the non-UB printing is selected."""
        mock_request.side_effect = [
            _named_response(SKRELV_UB_PRINTING),  # /cards/named
            _printings_response([SKRELV_NON_UB_PRINTING]),  # -is:ub filtered search
        ]

        card = scryfall.fetch_card(
            name="Skrelv, Defector Mite",
            ignore_ub=True,
        )

        assert card.set == 'one'
        assert card.collector_number == '255'

    @patch('plugins.mtg.scryfall._request_scryfall')
    def test_prefer_ub_falls_back_for_ub_only_card(self, mock_request):
        """With prefer_ub=True on a UB-only card, the UB printing is used after fallback."""
        mock_request.side_effect = [
            _named_response(EXCALIBUR),  # /cards/named
            _printings_response([]),  # is:ub → empty (no non-UB)
            _printings_response([EXCALIBUR]),  # fallback to all printings
        ]

        card = scryfall.fetch_card(
            name="Excalibur, Sword of Eden",
            ignore_ub=True,
        )

        assert card.set == 'acr'
        assert card.collector_number == '72'


class TestScryfallFetch:
    """Unit tests for Scryfall card fetching logic."""

    @patch('plugins.mtg.scryfall._request_scryfall')
    def test_flavor_name_card_is_fetched(self, mock_request):
        """A card known only by its flavor name still has its art fetched successfully."""
        mock_request.side_effect = [
            _make_404(),
            _printings_response([SHADOWSPEAR]),
        ]

        _ = scryfall.fetch_card(name="Donnie's Bō")

    @patch('plugins.mtg.scryfall.remote._session.get')
    def test_image_fetched_with_lowercase_set_code(self, mock_get):
        """When given an uppercase set code, the image is fetched using the lowercase code returned by the API."""
        mock_get.side_effect = [
            _named_response(_mk_card('Felidar Retreat', 'fdn', '574'))
        ]

        with patch('builtins.open', MagicMock()):
            card = scryfall.fetch_card(
                name="Felidar Retreat",
                set_code="FDN",
                collector_number="574",
            )

        assert card.set == 'fdn'
        assert card.collector_number == '574'

    @patch('plugins.mtg.scryfall._request_scryfall')
    def test_found_by_exact_name_does_not_call_flavor_search(self, mock_request):
        """When a card is found by its exact name, no additional flavor name search is made."""
        mock_request.return_value = _named_response(SHADOWSPEAR)

        _card = scryfall.fetch_card(name="Shadowspear")

        # Build a list of every URL string passed to request_scryfall across all calls.
        # call_args_list → list of calls, one per request_scryfall invocation
        # call[0]        → positional args tuple for that call
        # call[0][0]     → first positional argument, which is the URL string
        called_urls = [call[0][0] for call in mock_request.call_args_list]
        assert not any('flavor_name' in url for url in called_urls)


# --- Unit Tests for Language Support ---


class TestScryfallLanguageEnum:
    """Test MtgPrintedLanguage enum values and mapping to Scryfall API codes."""

    def test_all_printed_codes_present(self):
        """All supported printed codes are present in the enum."""
        expected_printed_codes = {
            "en",
            "sp",
            "fr",
            "de",
            "it",
            "pt",
            "jp",
            "kr",
            "ru",
            "cs",
            "ct",
            "ag",
            "ph",
        }
        assert len(MtgPrintedLanguage) == len(expected_printed_codes)
        for lang in expected_printed_codes:
            # test it both constructs and is an identity map
            assert MtgPrintedLanguage(lang).value == lang

    def test_print_injective_to_scryfall(self):
        """Printed language codes are injective to Scryfall language codes."""
        mapping = {
            scryfall.Language.from_printed_lang(code) for code in MtgPrintedLanguage
        }
        assert len(mapping) == len(MtgPrintedLanguage)

    def test_to_scryfall_api_lang_non_trivial_mappings(self):
        """Printed codes that differ from the Scryfall API code are mapped correctly."""
        expected_non_trivials = {
            MtgPrintedLanguage.ANCIENT_GREEK,
            MtgPrintedLanguage.JAPANESE,
            MtgPrintedLanguage.KOREAN,
            MtgPrintedLanguage.SIMPLIFIED_CHINESE,
            MtgPrintedLanguage.SPANISH,
            MtgPrintedLanguage.TRADITIONAL_CHINESE,
        }
        non_trivials = {
            code
            for code in MtgPrintedLanguage
            if scryfall.Language.from_printed_lang(code).value != code.value
        }
        assert non_trivials == expected_non_trivials


class TestBuildImageUrl:
    """Test URL construction for different language preferences."""

    def test_english_produces_default_url(self):
        url = _build_image_url("lea", "1", scryfall.Language.ENGLISH)
        assert url == "https://api.scryfall.com/cards/lea/1/?format=image&version=png"
        assert "/en?" not in url

    def test_non_english_embeds_api_lang_code(self):
        url = _build_image_url("lea", "1", scryfall.Language.JAPANESE)
        assert url == "https://api.scryfall.com/cards/lea/1/ja?format=image&version=png"

    def test_spanish_uses_api_code_not_printed_code(self):
        """Printed code 'sp' must map to API code 'es' in the URL."""
        url = _build_image_url("lea", "1", scryfall.Language.SPANISH)
        assert "/es?" in url
        assert "/sp?" not in url

    def test_simplified_chinese_uses_zhs(self):
        url = _build_image_url("lea", "1", scryfall.Language.SIMPLIFIED_CHINESE)
        assert "/zhs?" in url


class TestFetchImageLanguageFallback:
    """Test that fetch_image tries langs in priority order, falling back to English."""

    @patch('plugins.mtg.scryfall._request_scryfall')
    def test_falls_back_to_english_on_404(self, mock_request):
        lang_404 = requests.exceptions.HTTPError()
        lang_404.response = MagicMock()
        lang_404.response.status_code = 404

        english_response = MagicMock()
        english_response.content = b'fake_english_image'
        mock_request.side_effect = [lang_404, english_response]

        result = scryfall.fetch_image("neo", "26", [scryfall.Language.JAPANESE])

        assert result == b'fake_english_image'
        assert mock_request.call_count == 2
        fallback_url = mock_request.call_args_list[1][0][0]
        assert "/ja?" not in fallback_url
        assert "neo/26/" in fallback_url

    @patch('plugins.mtg.scryfall._request_scryfall')
    def test_tries_priority_order_before_english(self, mock_request):
        """With [jp, de], tries jp → de → en, returning first success."""
        err_404 = requests.exceptions.HTTPError()
        err_404.response = MagicMock()
        err_404.response.status_code = 404

        de_response = MagicMock()
        de_response.content = b'fake_german_image'
        mock_request.side_effect = [err_404, de_response]

        result = scryfall.fetch_image(
            "lea", "1", [scryfall.Language.JAPANESE, scryfall.Language.GERMAN]
        )

        assert result == b'fake_german_image'
        assert mock_request.call_count == 2
        second_url = mock_request.call_args_list[1][0][0]
        assert "/de?" in second_url

    @patch('plugins.mtg.scryfall._request_scryfall')
    def test_raises_when_all_langs_404(self, mock_request):
        """Raises the last HTTPError when every language including English 404s."""
        err_404 = requests.exceptions.HTTPError()
        err_404.response = MagicMock()
        err_404.response.status_code = 404
        mock_request.side_effect = err_404

        with pytest.raises(requests.exceptions.HTTPError):
            scryfall.fetch_image("lea", "1", [scryfall.Language.JAPANESE])

        assert mock_request.call_count == 2  # jp + en fallback

    @patch('plugins.mtg.scryfall._request_scryfall')
    def test_does_not_fall_back_on_non_404_error(self, mock_request):
        err_500 = requests.exceptions.HTTPError()
        err_500.response = MagicMock()
        err_500.response.status_code = 500
        mock_request.side_effect = err_500

        with pytest.raises(requests.exceptions.HTTPError):
            scryfall.fetch_image("neo", "26", [scryfall.Language.JAPANESE])

        assert mock_request.call_count == 1

    @patch('plugins.mtg.scryfall._request_scryfall')
    def test_english_only_does_not_retry_on_404(self, mock_request):
        err_404 = requests.exceptions.HTTPError()
        err_404.response = MagicMock()
        err_404.response.status_code = 404
        mock_request.side_effect = err_404

        with pytest.raises(requests.exceptions.HTTPError):
            scryfall.fetch_image("lea", "1", [scryfall.Language.ENGLISH])

        assert mock_request.call_count == 1

    @patch('plugins.mtg.scryfall._request_scryfall')
    def test_no_langs_falls_back_to_english(self, mock_request):
        english_response = MagicMock()
        english_response.content = b'fake_english_image'
        mock_request.return_value = english_response

        result = scryfall.fetch_image("lea", "1", [])

        assert result == b'fake_english_image'
        url = mock_request.call_args_list[0][0][0]
        assert "/en?" not in url  # English uses the default URL form


class TestFetchCardWithLanguage:
    """Test that fetch_card passes prefer_langs through to fetch_card_art."""

    @patch('plugins.mtg.scryfall._request_scryfall')
    def test_prefer_langs_passed_to_fetch_card_art(self, mock_request):
        skrlev_ub_ja = copy.copy(SKRELV_NON_UB_PRINTING)
        skrlev_ub_ja.lang = scryfall.Language.JAPANESE

        mock_request.side_effect = [
            _named_response(SKRELV_NON_UB_PRINTING),
            _printings_response([skrlev_ub_ja]),
        ]

        langs = [scryfall.Language.JAPANESE, scryfall.Language.GERMAN]
        card = scryfall.fetch_card(
            name="Shadowspear",
            prefer_langs=langs,
        )

        assert card.lang == scryfall.Language.JAPANESE


# --- Integration Tests for API and Image Fetching ---


@pytest.mark.integration
class TestScryfallAPI:
    """Test Scryfall API requests."""

    def test_scryfall_api_availability(self):
        """Test that Scryfall API is available and responding."""
        response = _request_scryfall(
            "https://api.scryfall.com/cards/named?exact=Lightning+Bolt"
        )
        assert response.status_code == 200
        card = from_json(Card, response.content)
        assert card.name == "Lightning Bolt"


@pytest.mark.integration
class TestFetchWorkflow:
    """Integration tests for the fetching workflow. Doesn't write to disk."""

    def test_fetch_single_card_simple_format(self):
        """Test fetching a single card using simple format."""

        deck_text = "Lightning Bolt"
        errs, deck = parse_deck(deck_text, DeckFormat.SIMPLE, scryfall.fetch_card)
        assert not errs
        assert len(deck) == 1
        assert list(deck.items())[0][1] == 1

        faces = scryfall.fetch_faces(list(deck.keys())[0])
        assert faces.back is None  # not a double sided card
        assert 0 < len(faces.front)

    def test_fetch_double_faced_card(self):
        """Test fetching a double-faced card."""

        deck_text = "1 Agadeem's Awakening // Agadeem, the Undercrypt (ZNR) 90"
        errs, deck = parse_deck(deck_text, DeckFormat.MTGA, scryfall.fetch_card)
        assert not errs
        assert len(deck) == 1
        assert list(deck.items())[0][1] == 1

        faces = scryfall.fetch_faces(list(deck.keys())[0])
        assert faces.back is not None  # double sided card
        assert 0 < len(faces.front)
        assert 0 < len(faces.back)

    def test_fetch_flavor_name_card(self):
        """Cards with flavor names (e.g. convention promos) resolve to the correct card art."""
        _card = scryfall.fetch_card(name="Donnie's Bō")

    def test_fetch_reversible_card(self):
        """Fetching a reversible_card saves both the front and back art."""

        # Anointed Procession (SLD) 1511 is a reversible_card layout — same card name/rules on both
        # sides, but with different artwork. Both faces should be downloaded.
        deck_text = "1 Anointed Procession (SLD) 1511"
        errs, deck = parse_deck(deck_text, DeckFormat.MTGA, scryfall.fetch_card)
        assert not errs
        assert len(deck) == 1

        faces = scryfall.fetch_faces(list(deck.keys())[0])
        assert faces.back is not None  # double sided card
        assert 0 < len(faces.front)
        assert 0 < len(faces.back)

    def test_fetch_meld_card(self):
        """Fetching a meld part saves its front art and a cropped half of the combined meld result as the back."""
        from PIL import Image

        # Bruna, the Fading Light is a meld part whose back is the top half of Brisela, Voice of Nightmares
        deck_text = "1 Bruna, the Fading Light (EMN) 15"
        errs, deck = parse_deck(deck_text, DeckFormat.MTGA, scryfall.fetch_card)
        assert not errs
        assert len(deck) == 1

        faces = scryfall.fetch_faces(list(deck.keys())[0])
        assert faces.back is not None  # double sided card
        assert 0 < len(faces.front)
        assert 0 < len(faces.back)

        # The saved back image should have full card dimensions (same width as the meld result image)
        front_img = Image.open(BytesIO(faces.front))
        back_img = Image.open(BytesIO(faces.back))
        assert back_img.size == front_img.size


@pytest.mark.integration
class TestFullFetchWorkflow:
    """Integration tests for the complete card fetching workflow."""

    @pytest.fixture
    def temp_dirs(self):
        """Create temporary directories for test output."""
        front_dir = tempfile.mkdtemp()
        double_sided_dir = tempfile.mkdtemp()
        yield front_dir, double_sided_dir
        shutil.rmtree(front_dir)
        shutil.rmtree(double_sided_dir)

    # TODO: add tests for new deck assembly routine


@pytest.mark.integration
class TestUniverseBeyondScryfallData:
    """Sanity checks that the Scryfall data for our test cards matches expectations.

    If these fail it means the cards have received new printings that change their
    UB/non-UB composition — update the URIs below and re-check the
    filtering tests, rather than assuming the plugin is broken.

    Oracle IDs verified from stable card IDs:
    - Skrelv: https://api.scryfall.com/cards/509c00d2-6a84-4760-8927-483ed123b05f
    - Excalibur: https://api.scryfall.com/cards/4e357b2d-a3c1-490e-a37c-cdf42abcfa60
    """

    SKRELV_PRINTS_URI = 'https://api.scryfall.com/cards/search?order=released&q=oracleid%3A20053847-6623-493c-8cdb-a69cda3b1577&unique=prints'
    EXCALIBUR_PRINTS_URI = 'https://api.scryfall.com/cards/search?order=released&q=oracleid%3A9fb6bd72-031b-40a1-83c5-8a1c82f84e12&unique=prints'

    def test_skrelv_has_ub_printing(self):
        """Scryfall still lists a UB printing of Skrelv (SLD 1926)."""
        printings = _fetch_printings(
            'Skrelv, Defector Mite', self.SKRELV_PRINTS_URI, None
        )
        sets = {p.set for p in printings}
        assert 'sld' in sets, (
            "Scryfall no longer lists SLD as a printing of Skrelv. "
            "Update the expected set codes in TestUniverseBeyondFiltering."
        )

    def test_skrelv_has_non_ub_printing(self):
        """Scryfall still lists a non-UB printing of Skrelv (ONE 225)."""
        printings = _fetch_printings(
            'Skrelv, Defector Mite', self.SKRELV_PRINTS_URI, None
        )
        sets = {p.set for p in printings}
        assert 'one' in sets, (
            "Scryfall no longer lists ONE as a printing of Skrelv. "
            "Update the expected set codes in TestUniverseBeyondFiltering."
        )

    def test_excalibur_is_ub_only(self):
        """Scryfall lists Excalibur only in UB sets — no non-UB printings exist."""
        all_printings = _fetch_printings(
            'Excalibur, Sword of Eden', self.EXCALIBUR_PRINTS_URI, None
        )
        non_ub_printings = _fetch_printings(
            'Excalibur, Sword of Eden', self.EXCALIBUR_PRINTS_URI, False
        )
        assert len(non_ub_printings) == len(all_printings), (
            "Excalibur now has a non-UB printing. It can no longer be used as the "
            "UB-only fallback test case — update TestUniverseBeyondFiltering."
        )


@pytest.mark.integration
class TestLanguagePrioritization:
    """Unit tests for language prioritization in progressive filtering.

    When prefer_langs is specified, the filtering logic should prioritize language
    BEFORE other aesthetic filters (showcase, extra_art, etc). This ensures users
    get cards in their preferred language even if fancier versions are only available
    in English.
    """

    @staticmethod
    def make_printing(
        set_code: SetCode,
        collector_number: CollectorNumber,
        lang: scryfall.Language = scryfall.Language.ENGLISH,
        full_art: bool = False,
        showcase: bool = False,
    ):
        """Helper to create a mock printing with specified attributes."""
        return _mk_card(
            name='',
            set=set_code,
            collector_number=collector_number,
            border_color=(
                scryfall.BorderColour.BORDERLESS
                if full_art
                else scryfall.BorderColour.BLACK
            ),
            frame_effects=[scryfall.FrameEffect.SHOWCASE] if showcase else [],
            full_art=full_art,
            lang=lang,
        )

    @patch('plugins.mtg.scryfall._request_scryfall')
    def test_prefer_german_over_english_full_art(self, mock_request):
        """When a card has English full-art and German normal versions, German is selected."""
        printings = [
            self.make_printing('lea', '1', scryfall.Language.ENGLISH, full_art=True),
            self.make_printing('lea', '2', scryfall.Language.GERMAN, full_art=False),
        ]
        mock_request.side_effect = [
            _named_response(_mk_card("Lightning Bolt", 'lea', '1')),
            _printings_response(printings),
        ]

        card = scryfall.fetch_card(
            name="Lightning Bolt",
            prefer_extra_art=True,
            prefer_langs=[scryfall.Language.GERMAN],
        )

        # Should select German printing even though English has full_art
        assert card.set == 'lea'
        assert card.collector_number == '2'  # German version

    @patch('plugins.mtg.scryfall._request_scryfall')
    def test_prefer_german_over_english_showcase(self, mock_request):
        """When a card has English showcase and German normal versions, German is selected."""
        printings = [
            self.make_printing(
                'lea', '1', scryfall.Language.ENGLISH, showcase=True
            ),  # English showcase
            self.make_printing(
                'lea', '2', scryfall.Language.GERMAN, showcase=False
            ),  # German normal
        ]
        mock_request.side_effect = [
            _named_response(_mk_card("Sol Ring", 'lea', '1')),
            _printings_response(printings),
        ]

        card = scryfall.fetch_card(
            name="Sol Ring",
            prefer_langs=[scryfall.Language.GERMAN],
            prefer_showcase=True,
        )

        # Should select German printing even though English has showcase
        assert card.set == 'lea'
        assert card.collector_number == '2'  # German version

    @patch('plugins.mtg.scryfall._request_scryfall')
    def test_prefer_german_showcase_over_german_normal(self, mock_request):
        """When both German showcase and German normal exist, German showcase is selected."""
        printings = [
            # English showcase
            self.make_printing('lea', '1', scryfall.Language.ENGLISH, showcase=True),
            # German normal
            self.make_printing('lea', '2', scryfall.Language.GERMAN, showcase=False),
            # German showcase
            self.make_printing('lea', '3', scryfall.Language.GERMAN, showcase=True),
        ]
        mock_request.side_effect = [
            _named_response(_mk_card("Path to Exile", 'lea', '1')),
            _printings_response(printings),
        ]

        card = scryfall.fetch_card(
            name="Path to Exile",
            prefer_langs=[scryfall.Language.GERMAN],
            prefer_showcase=True,
        )

        # Should select German showcase over German normal
        assert card.set == 'lea'
        assert card.collector_number == '3'  # German showcase

    @patch('plugins.mtg.scryfall._request_scryfall')
    def test_multiple_prefer_langs_with_priority(self, mock_request):
        """When prefer_langs=[GERMAN, FRENCH], German is preferred over French."""
        printings = [
            self.make_printing('lea', '1', scryfall.Language.ENGLISH),  # English
            self.make_printing('lea', '2', scryfall.Language.FRENCH),  # French
            self.make_printing('lea', '3', scryfall.Language.GERMAN),  # German
        ]
        mock_request.side_effect = [
            _named_response(_mk_card("Counterspell", 'lea', '1')),
            _printings_response(printings),
        ]
        card = scryfall.fetch_card(
            name="Counterspell",
            prefer_langs=[scryfall.Language.GERMAN, scryfall.Language.FRENCH],
        )

        # Should select German (first in prefer_langs) over French
        assert card.set == 'lea'
        assert card.lang == scryfall.Language.GERMAN

    @patch('plugins.mtg.scryfall._request_scryfall')
    def test_fallback_to_english_when_preferred_lang_unavailable(self, mock_request):
        """When preferred language is unavailable, falls back to English."""
        printings = [
            # English full-art (only option)
            self.make_printing('lea', '1', scryfall.Language.ENGLISH, full_art=True),
        ]
        mock_request.side_effect = [
            _named_response(_mk_card("Ancient Tomb", 'lea', '1')),
            _printings_response(printings),
        ]

        card = scryfall.fetch_card(
            name="Ancient Tomb",
            prefer_langs=[scryfall.Language.GERMAN],
        )

        # Should fall back to English when German is unavailable
        assert card.set == 'lea'
        assert card.lang == scryfall.Language.ENGLISH


@pytest.mark.integration
class TestUniverseBeyondFiltering:
    """Integration tests for prefer_ub and ignore_ub options via fetch_printings.

    Skrelv, Defector Mite exists as both a standard printing (ONE 225)
    and a Universe Beyond printing (SLD 1926).
    Excalibur, Sword of Eden only exists as a Universe Beyond printing (ACR 72).

    Oracle IDs verified from stable card IDs:
    - Skrelv: https://api.scryfall.com/cards/509c00d2-6a84-4760-8927-483ed123b05f
    - Excalibur: https://api.scryfall.com/cards/4e357b2d-a3c1-490e-a37c-cdf42abcfa60
    """

    SKRELV_PRINTS_URI = 'https://api.scryfall.com/cards/search?order=released&q=oracleid%3A20053847-6623-493c-8cdb-a69cda3b1577&unique=prints'
    EXCALIBUR_PRINTS_URI = 'https://api.scryfall.com/cards/search?order=released&q=oracleid%3A9fb6bd72-031b-40a1-83c5-8a1c82f84e12&unique=prints'

    def test_prefer_ub_returns_only_ub_printings(self):
        """prefer_ub=True returns only Universe Beyond printings of Skrelv."""
        printings = _fetch_printings(
            'Skrelv, Defector Mite', self.SKRELV_PRINTS_URI, True
        )

        sets = {p.set for p in printings}
        assert 'sld' in sets
        assert 'one' not in sets

    def test_ignore_ub_returns_only_non_ub_printings(self):
        """ignore_ub=True returns only non-Universe Beyond printings of Skrelv."""
        printings = _fetch_printings(
            'Skrelv, Defector Mite', self.SKRELV_PRINTS_URI, False
        )

        sets = {p.set for p in printings}
        assert 'sld' not in sets
        assert 'one' in sets

    def test_no_filter_returns_all_printings(self):
        """prefer_ub=None returns all printings including both UB and non-UB."""
        printings = _fetch_printings(
            'Skrelv, Defector Mite', self.SKRELV_PRINTS_URI, None
        )

        sets = {p.set for p in printings}
        assert 'one' in sets
        assert 'sld' in sets

    def test_ignore_ub_falls_back_for_ub_only_card(self):
        """ignore_ub=True falls back to all printings when every printing is UB."""
        printings = _fetch_printings(
            'Excalibur, Sword of Eden', self.EXCALIBUR_PRINTS_URI, False
        )

        # Fallback: should still return printings rather than an empty list
        assert len(printings) > 0
        assert any(p.set == 'acr' for p in printings)
