"""
Tests for the Grand Archive plugin.
Tests deck format parsing and image fetching from gatcg.com.
"""
import os
import shutil
import tempfile
import pytest

from plugins.grand_archive.deck_formats import DeckFormat, parse_deck, parse_omnideck
from plugins.grand_archive.gatcg import request_gatcg, get_handle_card


# --- Unit Tests for Deck Format Parsing ---

class TestOmnideckFormat:
    """Test Omnideck format parsing."""

    def test_parse_omnideck_basic(self):
        """Test parsing basic Omnideck format."""
        deck_text = """# Main Deck
3 Incapacitate
4 Sable Remnant
4 Slice and Dice"""

        parsed_cards = []
        def collect_card(index, card_name, quantity):
            parsed_cards.append({
                'index': index,
                'card_name': card_name,
                'quantity': quantity
            })

        parse_omnideck(deck_text, collect_card)

        assert len(parsed_cards) == 3
        assert parsed_cards[0]['card_name'] == "Incapacitate"
        assert parsed_cards[0]['quantity'] == 3
        assert parsed_cards[1]['card_name'] == "Sable Remnant"
        assert parsed_cards[1]['quantity'] == 4

    def test_parse_omnideck_with_material_deck(self):
        """Test parsing Omnideck format with material deck section."""
        deck_text = """# Main Deck
3 Incapacitate
4 Dream Fairy

# Material Deck
1 Spirit of Wind
1 Tristan, Underhanded"""

        parsed_cards = []
        def collect_card(index, card_name, quantity):
            parsed_cards.append({
                'index': index,
                'card_name': card_name,
                'quantity': quantity
            })

        parse_omnideck(deck_text, collect_card)

        assert len(parsed_cards) == 4
        assert parsed_cards[2]['card_name'] == "Spirit of Wind"
        assert parsed_cards[3]['card_name'] == "Tristan, Underhanded"

    def test_parse_omnideck_skips_comments(self):
        """Test that Omnideck parsing skips comment lines."""
        deck_text = """# Main Deck
3 Incapacitate
# This is a comment
4 Dream Fairy"""

        parsed_cards = []
        def collect_card(index, card_name, quantity):
            parsed_cards.append({
                'index': index,
                'card_name': card_name,
                'quantity': quantity
            })

        parse_omnideck(deck_text, collect_card)

        assert len(parsed_cards) == 2


# --- Integration Tests for API and Image Fetching ---

@pytest.mark.integration
class TestGatcgAPI:
    """Test Grand Archive TCG API requests."""

    def test_gatcg_api_availability(self):
        """Test that Grand Archive API is available and responding."""
        response = request_gatcg("https://api.gatcg.com/api/cards?search=incapacitate")
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
        """Test fetching a single Grand Archive card."""
        front_dir = temp_dirs

        # Use a very small decklist - just 1 card
        deck_text = "1 Dream Fairy"

        handle_card = get_handle_card(front_dir)
        parse_deck(deck_text, DeckFormat.OMNIDECK, handle_card)

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

        deck_text = "2 Dream Fairy"

        handle_card = get_handle_card(front_dir)
        parse_deck(deck_text, DeckFormat.OMNIDECK, handle_card)

        # Should have 2 copies of the card
        files = os.listdir(front_dir)
        assert len(files) == 2

        for f in files:
            file_path = os.path.join(front_dir, f)
            assert os.path.getsize(file_path) > 0
