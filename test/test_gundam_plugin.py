"""
Tests for the Gundam plugin.
Tests deck format parsing and image fetching.
"""
import os
import shutil
import tempfile
import pytest

from plugins.gundam.deck_formats import (
    DeckFormat,
    parse_deck,
    parse_deckplanet,
    parse_limitless,
    parse_egman,
    parse_exburst,
)
from plugins.gundam.gundam import request_bandai, get_handle_card


# --- Unit Tests for Deck Format Parsing ---

class TestDeckplanetFormat:
    """Test DeckPlanet format parsing."""

    def test_parse_deckplanet(self):
        """Test parsing DeckPlanet format."""
        deck_text = """2 Guntank [GD01-008]
4 Gundam (MA Form) [ST01-002]
4 Demi Trainer [ST01-008]"""

        parsed_cards = []
        def collect_card(index, card_number, quantity):
            parsed_cards.append({
                'index': index,
                'card_number': card_number,
                'quantity': quantity
            })

        parse_deckplanet(deck_text, collect_card)

        assert len(parsed_cards) == 3
        assert parsed_cards[0]['card_number'] == "GD01-008"
        assert parsed_cards[0]['quantity'] == 2
        assert parsed_cards[1]['card_number'] == "ST01-002"


class TestLimitlessFormat:
    """Test Limitless TCG format parsing."""

    def test_parse_limitless(self):
        """Test parsing Limitless TCG format."""
        deck_text = """4 Dopp GD01-039
4 Zaku Ⅰ ST03-007
3 Guntank GD01-008"""

        parsed_cards = []
        def collect_card(index, card_number, quantity):
            parsed_cards.append({
                'index': index,
                'card_number': card_number,
                'quantity': quantity
            })

        parse_limitless(deck_text, collect_card)

        assert len(parsed_cards) == 3
        assert parsed_cards[0]['card_number'] == "GD01-039"
        assert parsed_cards[0]['quantity'] == 4


class TestEgmanFormat:
    """Test Egman Events format parsing."""

    def test_parse_egman(self):
        """Test parsing Egman Events format."""
        deck_text = """4 GD01-039 Dopp
4 ST03-007 Zaku I | MS-05
4 GD01-035 Zaku II | MS-06"""

        parsed_cards = []
        def collect_card(index, card_number, quantity):
            parsed_cards.append({
                'index': index,
                'card_number': card_number,
                'quantity': quantity
            })

        parse_egman(deck_text, collect_card)

        assert len(parsed_cards) == 3
        assert parsed_cards[0]['card_number'] == "GD01-039"
        assert parsed_cards[1]['card_number'] == "ST03-007"


class TestExburstFormat:
    """Test ExBurst format parsing."""

    def test_parse_exburst(self):
        """Test parsing ExBurst format."""
        deck_text = """4 x ST04-008
4 x ST01-005
4 x GD01-059"""

        parsed_cards = []
        def collect_card(index, card_number, quantity):
            parsed_cards.append({
                'index': index,
                'card_number': card_number,
                'quantity': quantity
            })

        parse_exburst(deck_text, collect_card)

        assert len(parsed_cards) == 3
        assert parsed_cards[0]['card_number'] == "ST04-008"
        assert parsed_cards[0]['quantity'] == 4


# --- Integration Tests for API and Image Fetching ---

class TestGundamAPI:
    """Test Gundam API requests."""

    def test_gundam_api_availability(self):
        """Test that Gundam card images are available."""
        # Test with a known card number
        response = request_bandai("https://www.gundam-tcg.com/assets/images/cardlist/en/ST01-001.png")
        assert response.status_code == 200


class TestFullFetchWorkflow:
    """Integration tests for the complete card fetching workflow."""

    @pytest.fixture
    def temp_dirs(self):
        """Create temporary directories for test output."""
        front_dir = tempfile.mkdtemp()
        yield front_dir
        shutil.rmtree(front_dir)

    def test_fetch_single_card_deckplanet(self, temp_dirs):
        """Test fetching a single card using DeckPlanet format."""
        front_dir = temp_dirs

        # Use a very small decklist - just 1 card
        deck_text = "1 Gundam [ST01-001]"

        handle_card = get_handle_card(front_dir)
        parse_deck(deck_text, DeckFormat.DECKPLANET, handle_card)

        # Check that at least one image was created
        files = os.listdir(front_dir)
        assert len(files) >= 1

        # Verify image file has content (> 0 bytes)
        for f in files:
            file_path = os.path.join(front_dir, f)
            assert os.path.getsize(file_path) > 0

    def test_fetch_single_card_exburst(self, temp_dirs):
        """Test fetching a single card using ExBurst format."""
        front_dir = temp_dirs

        deck_text = "1 x ST01-001"

        handle_card = get_handle_card(front_dir)
        parse_deck(deck_text, DeckFormat.EXBURST, handle_card)

        files = os.listdir(front_dir)
        assert len(files) >= 1

        for f in files:
            file_path = os.path.join(front_dir, f)
            assert os.path.getsize(file_path) > 0
