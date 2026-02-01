"""
Tests for the Altered plugin.
Tests deck format parsing and image fetching from Altered.
"""
import os
import shutil
import tempfile
import pytest

from plugins.altered.deck_formats import DeckFormat, parse_deck, parse_ajordat
from plugins.altered.altered import request_altered, get_handle_card


# --- Unit Tests for Deck Format Parsing ---

class TestAjordatFormat:
    """Test Ajordat format parsing."""

    def test_parse_ajordat_basic(self):
        """Test parsing basic Ajordat format."""
        deck_text = """1 ALT_COREKS_B_OR_01_C
3 ALT_ALIZE_B_MU_31_R2
2 ALT_ALIZE_B_OR_42_R1"""

        parsed_cards = []
        def collect_card(index, qr_code, quantity):
            parsed_cards.append({
                'index': index,
                'qr_code': qr_code,
                'quantity': quantity
            })

        parse_ajordat(deck_text, collect_card)

        assert len(parsed_cards) == 3
        assert parsed_cards[0]['qr_code'] == "ALT_COREKS_B_OR_01_C"
        assert parsed_cards[0]['quantity'] == 1
        assert parsed_cards[1]['qr_code'] == "ALT_ALIZE_B_MU_31_R2"
        assert parsed_cards[1]['quantity'] == 3

    def test_parse_ajordat_with_unique_suffix(self):
        """Test parsing Ajordat format with unique card suffixes."""
        deck_text = """1 ALT_CORE_B_OR_20_U_7022
1 ALT_COREKS_B_BR_09_U_4235"""

        parsed_cards = []
        def collect_card(index, qr_code, quantity):
            parsed_cards.append({
                'index': index,
                'qr_code': qr_code,
                'quantity': quantity
            })

        parse_ajordat(deck_text, collect_card)

        assert len(parsed_cards) == 2
        assert parsed_cards[0]['qr_code'] == "ALT_CORE_B_OR_20_U_7022"


# --- Integration Tests for API and Image Fetching ---

class TestAlteredAPI:
    """Test Altered API requests."""

    def test_altered_api_availability(self):
        """Test that Altered API is available and responding."""
        # Test with a known card QR code
        response = request_altered("https://api.altered.gg/cards/ALT_COREKS_B_OR_01_C")
        assert response.status_code == 200


class TestFullFetchWorkflow:
    """Integration tests for the complete card fetching workflow."""

    @pytest.fixture
    def temp_dirs(self):
        """Create temporary directories for test output."""
        front_dir = tempfile.mkdtemp()
        yield front_dir
        shutil.rmtree(front_dir)

    def test_fetch_single_card(self, temp_dirs):
        """Test fetching a single Altered card."""
        front_dir = temp_dirs

        # Use a very small decklist - just 1 card
        deck_text = "1 ALT_COREKS_B_OR_01_C"

        handle_card = get_handle_card(front_dir)
        parse_deck(deck_text, DeckFormat.AJORDAT, handle_card)

        # Check that at least one image was created
        files = os.listdir(front_dir)
        assert len(files) >= 1

        # Verify image file has content (> 0 bytes)
        for f in files:
            file_path = os.path.join(front_dir, f)
            assert os.path.getsize(file_path) > 0

    def test_fetch_with_quantity(self, temp_dirs):
        """Test fetching cards with quantity > 1."""
        front_dir = temp_dirs

        deck_text = "2 ALT_CORE_B_OR_08_C"

        handle_card = get_handle_card(front_dir)
        parse_deck(deck_text, DeckFormat.AJORDAT, handle_card)

        # Should have 2 copies of the card
        files = os.listdir(front_dir)
        assert len(files) == 2

        for f in files:
            file_path = os.path.join(front_dir, f)
            assert os.path.getsize(file_path) > 0
