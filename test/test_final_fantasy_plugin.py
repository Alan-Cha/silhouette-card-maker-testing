"""
Tests for the Final Fantasy TCG plugin.
Tests deck format parsing and image fetching from Square Enix.
"""
import os
import shutil
import tempfile
import pytest

from plugins.final_fantasy.deck_formats import DeckFormat, parse_deck, parse_untap, parse_octgn, parse_tts
from plugins.final_fantasy.fftcg import get_card_art_from_fftcg, request_fftcg, get_handle_card


# --- Unit Tests for Deck Format Parsing ---

class TestUntapFormat:
    """Test Untap/TTS format parsing."""

    def test_parse_untap_basic(self):
        """Test parsing basic Untap format."""
        deck_text = "1 Cloud (1-038R)\n2 Sol (1-002C)"

        parsed_cards = []
        def collect_card(index, name, serial_code, quantity):
            parsed_cards.append({
                'index': index,
                'name': name,
                'serial_code': serial_code,
                'quantity': quantity
            })

        parse_untap(deck_text, collect_card)

        assert len(parsed_cards) == 2
        assert parsed_cards[0]['name'] == "Cloud"
        assert parsed_cards[0]['serial_code'] == "1-038R"
        assert parsed_cards[0]['quantity'] == 1
        assert parsed_cards[1]['name'] == "Sol"
        assert parsed_cards[1]['serial_code'] == "1-002C"
        assert parsed_cards[1]['quantity'] == 2

    def test_parse_untap_skips_non_matching_lines(self):
        """Test that non-matching lines are skipped."""
        deck_text = "1 Cloud (1-038R)\nThis is a comment\n2 Sol (1-002C)"

        parsed_cards = []
        def collect_card(index, name, serial_code, quantity):
            parsed_cards.append({'name': name})

        parse_untap(deck_text, collect_card)

        assert len(parsed_cards) == 2

    def test_untap_line_pattern(self):
        """Test that the Untap format line pattern matches correctly."""
        import re
        pattern = re.compile(r'^(\d+)\s(.+)\s\((.+)\)$')

        assert pattern.match("1 Cloud (1-038R)")
        assert pattern.match("3 Shantotto (1-059L)")

        assert not pattern.match("")
        assert not pattern.match("Cloud (1-038R)")  # No quantity
        assert not pattern.match("1 Cloud")  # No serial code


class TestOCTGNFormat:
    """Test OCTGN XML format parsing."""

    def test_parse_octgn_basic(self):
        """Test parsing OCTGN XML format."""
        deck_text = """<deck>
  <section name="Main Deck">
    <card qty="1">Cloud (FFBE)</card>
    <card qty="2">Sol</card>
  </section>
</deck>"""

        parsed_cards = []
        def collect_card(index, name, serial_code, quantity, category=''):
            parsed_cards.append({
                'index': index,
                'name': name,
                'quantity': quantity,
                'category': category
            })

        parse_octgn(deck_text, collect_card)

        assert len(parsed_cards) == 2
        assert parsed_cards[0]['name'] == "Cloud"
        assert parsed_cards[0]['category'] == "FFBE"
        assert parsed_cards[0]['quantity'] == 1
        assert parsed_cards[1]['name'] == "Sol"
        assert parsed_cards[1]['category'] == ""
        assert parsed_cards[1]['quantity'] == 2

    def test_parse_octgn_multiple_sections(self):
        """Test parsing OCTGN format with multiple sections."""
        deck_text = """<deck>
  <section name="Main Deck">
    <card qty="1">Cloud</card>
  </section>
  <section name="Backup Deck">
    <card qty="3">Tidus</card>
  </section>
</deck>"""

        parsed_cards = []
        def collect_card(index, name, serial_code, quantity, category=''):
            parsed_cards.append({'name': name, 'quantity': quantity})

        parse_octgn(deck_text, collect_card)

        assert len(parsed_cards) == 2
        assert parsed_cards[0]['name'] == "Cloud"
        assert parsed_cards[1]['name'] == "Tidus"
        assert parsed_cards[1]['quantity'] == 3

    def test_parse_octgn_no_category(self):
        """Test parsing OCTGN format cards without a category tag."""
        deck_text = """<deck>
  <section name="Main Deck">
    <card qty="3">Tidus</card>
  </section>
</deck>"""

        parsed_cards = []
        def collect_card(index, name, serial_code, quantity, category=''):
            parsed_cards.append({'name': name, 'category': category})

        parse_octgn(deck_text, collect_card)

        assert len(parsed_cards) == 1
        assert parsed_cards[0]['name'] == "Tidus"
        assert parsed_cards[0]['category'] == ""


class TestTTSFormat:
    """Test Tabletop Simulator format parsing (alias for Untap format)."""

    def test_parse_tts_basic(self):
        """Test that TTS format parses identically to Untap format."""
        deck_text = "1 Cloud (1-038R)\n2 Sol (1-002C)"

        parsed_cards = []
        def collect_card(index, name, serial_code, quantity):
            parsed_cards.append({
                'name': name,
                'serial_code': serial_code,
                'quantity': quantity
            })

        parse_tts(deck_text, collect_card)

        assert len(parsed_cards) == 2
        assert parsed_cards[0]['name'] == "Cloud"
        assert parsed_cards[0]['serial_code'] == "1-038R"
        assert parsed_cards[0]['quantity'] == 1
        assert parsed_cards[1]['name'] == "Sol"
        assert parsed_cards[1]['serial_code'] == "1-002C"
        assert parsed_cards[1]['quantity'] == 2


class TestParseDeck:
    """Test parse_deck routing to correct format parsers."""

    def test_parse_deck_routes_untap(self):
        """Test that DeckFormat.UNTAP routes to the untap parser."""
        deck_text = "3 Shantotto (1-059L)"

        parsed_cards = []
        def collect_card(index, name, serial_code, quantity):
            parsed_cards.append({'name': name, 'serial_code': serial_code, 'quantity': quantity})

        parse_deck(deck_text, DeckFormat.UNTAP, collect_card)

        assert len(parsed_cards) == 1
        assert parsed_cards[0]['name'] == "Shantotto"
        assert parsed_cards[0]['serial_code'] == "1-059L"
        assert parsed_cards[0]['quantity'] == 3

    def test_parse_deck_routes_octgn(self):
        """Test that DeckFormat.OCTGN_XML routes to the OCTGN parser."""
        deck_text = """<deck><section name="Main"><card qty="2">Cloud</card></section></deck>"""

        parsed_cards = []
        def collect_card(index, name, serial_code, quantity, category=''):
            parsed_cards.append({'name': name, 'quantity': quantity})

        parse_deck(deck_text, DeckFormat.OCTGN_XML, collect_card)

        assert len(parsed_cards) == 1
        assert parsed_cards[0]['name'] == "Cloud"
        assert parsed_cards[0]['quantity'] == 2

    def test_parse_deck_routes_tts(self):
        """Test that DeckFormat.TABLETOP_SIMULATOR routes to the TTS/untap parser."""
        deck_text = "1 Cloud (1-038R)"

        parsed_cards = []
        def collect_card(index, name, serial_code, quantity):
            parsed_cards.append({'name': name})

        parse_deck(deck_text, DeckFormat.TABLETOP_SIMULATOR, collect_card)

        assert len(parsed_cards) == 1
        assert parsed_cards[0]['name'] == "Cloud"

    def test_parse_deck_unknown_format_raises(self):
        """Test that an unrecognised format raises ValueError."""
        with pytest.raises(ValueError):
            parse_deck("1 Cloud (1-038R)", "unknown_format", lambda *args: None)


# --- Integration Tests for API and Image Fetching ---

@pytest.mark.integration
class TestFFTCGAPI:
    """Test Final Fantasy TCG API requests."""

    def test_fftcg_api_availability(self):
        """Test that the FFTCG card API is available and responding."""
        from requests import post

        payload = {
            'language': 'en',
            'text': '',
            'type': [], 'element': [], 'cost': [], 'rarity': [],
            'power': [], 'category_1': [], 'set': [],
            'multicard': '', 'ex_burst': '',
            'code': '1-038R',
            'special': '', 'exactmatch': 1
        }
        r = post(
            "https://fftcg.square-enix-games.com/na/get-cards",
            json=payload,
            headers={'user-agent': 'silhouette-card-maker/0.1', 'accept': '*/*'}
        )
        assert r.status_code == 200
        data = r.json()
        assert 'cards' in data
        assert len(data['cards']) > 0

    def test_name_with_serial_code_returns_no_results(self):
        """Test that the FFTCG API returns no results when both name and code are provided.

        This documents the API quirk that necessitates searching by code only when
        a serial code is available (see fftcg.py get_card_art_from_fftcg).
        """
        from requests import post

        payload = {
            'language': 'en',
            'text': 'Cloud',
            'type': [], 'element': [], 'cost': [], 'rarity': [],
            'power': [], 'category_1': [], 'set': [],
            'multicard': '', 'ex_burst': '',
            'code': '1-038R',
            'special': '', 'exactmatch': 1
        }
        r = post(
            "https://fftcg.square-enix-games.com/na/get-cards",
            json=payload,
            headers={'user-agent': 'silhouette-card-maker/0.1', 'accept': '*/*'}
        )
        assert r.status_code == 200
        data = r.json()
        assert len(data.get('cards', [])) == 0

    def test_get_card_art_url(self):
        """Test fetching a card art URL from the FFTCG API."""
        # Search by serial code only (name+code together is unreliable in the FFTCG API)
        url = get_card_art_from_fftcg("", "1-038R")
        assert url is not None
        assert url.startswith("http")


@pytest.mark.integration
class TestFullFetchWorkflow:
    """Integration tests for the complete card fetching workflow."""

    @pytest.fixture
    def temp_dirs(self):
        """Create temporary directories for test output."""
        front_dir = tempfile.mkdtemp()
        yield front_dir
        shutil.rmtree(front_dir)

    def test_fetch_single_card_untap(self, temp_dirs):
        """Test fetching a single Final Fantasy card using Untap format."""
        front_dir = temp_dirs

        deck_text = "1 Cloud (1-038R)"

        handle_card = get_handle_card(front_dir)
        parse_deck(deck_text, DeckFormat.UNTAP, handle_card)

        files = os.listdir(front_dir)
        assert len(files) >= 1

        for f in files:
            file_path = os.path.join(front_dir, f)
            assert os.path.getsize(file_path) > 0

    def test_fetch_with_quantity(self, temp_dirs):
        """Test that quantity > 1 fetches and saves multiple copies of the card."""
        front_dir = temp_dirs

        deck_text = "2 Cloud (1-038R)"

        handle_card = get_handle_card(front_dir)
        parse_deck(deck_text, DeckFormat.UNTAP, handle_card)

        files = os.listdir(front_dir)
        assert len(files) == 2

        for f in files:
            file_path = os.path.join(front_dir, f)
            assert os.path.getsize(file_path) > 0

    def test_fetch_single_card_octgn(self, temp_dirs):
        """Test fetching a single Final Fantasy card using OCTGN format."""
        front_dir = temp_dirs

        deck_text = """<deck>
  <section name="Main Deck">
    <card qty="1">Cloud</card>
  </section>
</deck>"""

        handle_card = get_handle_card(front_dir)
        parse_deck(deck_text, DeckFormat.OCTGN_XML, handle_card)

        files = os.listdir(front_dir)
        assert len(files) >= 1

        for f in files:
            file_path = os.path.join(front_dir, f)
            assert os.path.getsize(file_path) > 0
