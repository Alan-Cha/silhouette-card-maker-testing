"""
Tests for the One Piece plugin.
Tests deck format parsing and image fetching.
"""
import os
import shutil
import tempfile
import pytest

from plugins.one_piece.deck_formats import DeckFormat, parse_deck, parse_optcgsim, parse_egman
from plugins.one_piece.one_piece import request_bandai, get_handle_card


# --- Unit Tests for Deck Format Parsing ---

class TestOptcgsimFormat:
    """Test OPTCG Simulator format parsing."""

    def test_parse_optcgsim(self):
        """Test parsing OPTCG Simulator format."""
        deck_text = """1xOP12-001
4xOP01-016
2xOP02-015"""

        parsed_cards = []
        def collect_card(index, card_code, quantity):
            parsed_cards.append({
                'index': index,
                'card_code': card_code,
                'quantity': quantity
            })

        parse_optcgsim(deck_text, collect_card)

        assert len(parsed_cards) == 3
        assert parsed_cards[0]['card_code'] == "OP12-001"
        assert parsed_cards[0]['quantity'] == 1
        assert parsed_cards[1]['card_code'] == "OP01-016"
        assert parsed_cards[1]['quantity'] == 4


class TestEgmanFormat:
    """Test Egman Events format parsing."""

    def test_parse_egman(self):
        """Test parsing Egman Events format."""
        deck_text = """4 OP01-016 Nami
4 OP03-008 Buggy
2 OP06-018 Gum-Gum King Kong Gatling"""

        parsed_cards = []
        def collect_card(index, card_code, quantity):
            parsed_cards.append({
                'index': index,
                'card_code': card_code,
                'quantity': quantity
            })

        parse_egman(deck_text, collect_card)

        assert len(parsed_cards) == 3
        assert parsed_cards[0]['card_code'] == "OP01-016"
        assert parsed_cards[0]['quantity'] == 4
        assert parsed_cards[1]['card_code'] == "OP03-008"


# --- Integration Tests for API and Image Fetching ---

@pytest.mark.integration
class TestOnePieceAPI:
    """Test One Piece API requests."""

    def test_onepiece_api_availability(self):
        """Test that One Piece card images are available."""
        # Test with a known card - using the official OPTCG image endpoint
        response = request_bandai("https://en.onepiece-cardgame.com/images/cardlist/card/OP01-016.png")
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

    def test_fetch_single_card_optcgsim(self, temp_dirs):
        """Test fetching a single card using OPTCG Simulator format."""
        front_dir = temp_dirs

        # Use a very small decklist - just 1 card
        deck_text = "1xOP01-016"

        handle_card = get_handle_card(front_dir)
        parse_deck(deck_text, DeckFormat.OPTCGSIMULATOR, handle_card)

        # Check that at least one image was created
        files = os.listdir(front_dir)
        assert len(files) >= 1

        # Verify image file has content (> 0 bytes)
        for f in files:
            file_path = os.path.join(front_dir, f)
            assert os.path.getsize(file_path) > 0

    def test_fetch_single_card_egman(self, temp_dirs):
        """Test fetching a single card using Egman format."""
        front_dir = temp_dirs

        deck_text = "1 OP01-016 Nami"

        handle_card = get_handle_card(front_dir)
        parse_deck(deck_text, DeckFormat.EGMANEVENTS, handle_card)

        files = os.listdir(front_dir)
        assert len(files) >= 1

        for f in files:
            file_path = os.path.join(front_dir, f)
            assert os.path.getsize(file_path) > 0
