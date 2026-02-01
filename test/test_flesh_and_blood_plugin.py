"""
Tests for the Flesh and Blood plugin.
Tests deck format parsing and image fetching from Fabrary/fabtcg.
"""
import os
import shutil
import tempfile
import pytest

from plugins.flesh_and_blood.deck_formats import DeckFormat, parse_deck, parse_fabrary, Pitch
from plugins.flesh_and_blood.fabtcg import request_fabtcg, get_handle_card


# --- Unit Tests for Deck Format Parsing ---

class TestFabraryFormat:
    """Test Fabrary format parsing."""

    def test_parse_fabrary_basic(self):
        """Test parsing basic Fabrary format."""
        deck_text = """1x Blood Splattered Vest
2x Kunai of Retribution
1x Mask of Momentum"""

        parsed_cards = []
        def collect_card(index, name, pitch, quantity):
            parsed_cards.append({
                'index': index,
                'name': name,
                'pitch': pitch,
                'quantity': quantity
            })

        parse_fabrary(deck_text, collect_card)

        assert len(parsed_cards) == 3
        assert parsed_cards[0]['name'] == "Blood Splattered Vest"
        assert parsed_cards[0]['pitch'] == Pitch.NONE
        assert parsed_cards[0]['quantity'] == 1
        assert parsed_cards[1]['name'] == "Kunai of Retribution"
        assert parsed_cards[1]['quantity'] == 2

    def test_parse_fabrary_with_pitch(self):
        """Test parsing Fabrary format with pitch values."""
        deck_text = """3x Ancestral Empowerment (red)
1x Salt the Wound (yellow)
2x Concealed Blade (blue)"""

        parsed_cards = []
        def collect_card(index, name, pitch, quantity):
            parsed_cards.append({
                'index': index,
                'name': name,
                'pitch': pitch,
                'quantity': quantity
            })

        parse_fabrary(deck_text, collect_card)

        assert len(parsed_cards) == 3
        assert parsed_cards[0]['name'] == "Ancestral Empowerment"
        assert parsed_cards[0]['pitch'] == Pitch.RED
        assert parsed_cards[1]['name'] == "Salt the Wound"
        assert parsed_cards[1]['pitch'] == Pitch.YELLOW
        assert parsed_cards[2]['name'] == "Concealed Blade"
        assert parsed_cards[2]['pitch'] == Pitch.BLUE

    def test_parse_fabrary_skips_headers(self):
        """Test that Fabrary parsing skips header lines."""
        deck_text = """Name: Test Deck
Hero: Cindra, Dracai of Retribution
Format: Classic Constructed

Arena cards
1x Blood Splattered Vest

Deck cards
3x Ancestral Empowerment (red)"""

        parsed_cards = []
        def collect_card(index, name, pitch, quantity):
            parsed_cards.append({
                'index': index,
                'name': name,
                'pitch': pitch,
                'quantity': quantity
            })

        parse_fabrary(deck_text, collect_card)

        # Should only parse the actual card lines
        assert len(parsed_cards) == 2
        assert parsed_cards[0]['name'] == "Blood Splattered Vest"
        assert parsed_cards[1]['name'] == "Ancestral Empowerment"


# --- Unit Tests for Pitch Enum ---

class TestPitchEnum:
    """Test Pitch enum values."""

    def test_pitch_values(self):
        """Test Pitch enum has correct values."""
        assert Pitch.RED.value == '1'
        assert Pitch.YELLOW.value == '2'
        assert Pitch.BLUE.value == '3'
        assert Pitch.NONE.value == ''


# --- Integration Tests for API and Image Fetching ---

@pytest.mark.integration
class TestFabtcgAPI:
    """Test FabTCG API requests."""

    def test_fabtcg_api_availability(self):
        """Test that FabTCG API is available and responding."""
        response = request_fabtcg("https://api.fabdb.net/cards?q=sink+below")
        assert response.status_code == 200


@pytest.mark.integration
class TestFullFetchWorkflow:
    """Integration tests for the complete card fetching workflow."""

    @pytest.fixture
    def temp_dirs(self):
        """Create temporary directories for test output."""
        front_dir = tempfile.mkdtemp()
        yield front_dir
        shutil.rmtree(front_dir)

    def test_fetch_single_card(self, temp_dirs):
        """Test fetching a single Flesh and Blood card."""
        front_dir = temp_dirs

        # Use a very small decklist - just 1 card without pitch
        deck_text = "1x Mask of Momentum"

        handle_card = get_handle_card(front_dir)
        parse_deck(deck_text, DeckFormat.FABRARY, handle_card)

        # Check that at least one image was created
        files = os.listdir(front_dir)
        assert len(files) >= 1

        # Verify image file has content (> 0 bytes)
        for f in files:
            file_path = os.path.join(front_dir, f)
            assert os.path.getsize(file_path) > 0

    def test_fetch_card_with_pitch(self, temp_dirs):
        """Test fetching a card with pitch value."""
        front_dir = temp_dirs

        deck_text = "1x Sink Below (red)"

        handle_card = get_handle_card(front_dir)
        parse_deck(deck_text, DeckFormat.FABRARY, handle_card)

        files = os.listdir(front_dir)
        assert len(files) >= 1

        for f in files:
            file_path = os.path.join(front_dir, f)
            assert os.path.getsize(file_path) > 0
