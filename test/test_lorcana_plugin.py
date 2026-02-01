"""
Tests for the Lorcana plugin.
Tests deck format parsing and image fetching from Lorcast.
"""
import os
import shutil
import tempfile
import pytest

from plugins.lorcana.deck_formats import DeckFormat, parse_deck, parse_dreamborn_list
from plugins.lorcana.lorcast import request_lorcast, get_handle_card, format_lorcast_query, remove_nonalphanumeric


# --- Unit Tests for Deck Format Parsing ---

class TestDreambornFormat:
    """Test Dreamborn format parsing."""

    def test_parse_dreamborn_basic(self):
        """Test parsing basic Dreamborn format."""
        deck_text = """1 Elsa, Spirit of Winter
4 Magic Broom, Illuminary Keeper
2 Diablo - Obedient Raven"""

        parsed_cards = []
        def collect_card(index, name, enchanted, quantity):
            parsed_cards.append({
                'index': index,
                'name': name,
                'enchanted': enchanted,
                'quantity': quantity
            })

        parse_dreamborn_list(deck_text, collect_card)

        assert len(parsed_cards) == 3
        assert parsed_cards[0]['name'] == "Elsa, Spirit of Winter"
        assert parsed_cards[0]['enchanted'] == False
        assert parsed_cards[0]['quantity'] == 1
        assert parsed_cards[1]['name'] == "Magic Broom, Illuminary Keeper"
        assert parsed_cards[1]['quantity'] == 4

    def test_parse_dreamborn_with_enchanted(self):
        """Test parsing Dreamborn format with enchanted marker."""
        deck_text = """1 Anna - True-Hearted *E*
2 Elsa, Spirit of Winter"""

        parsed_cards = []
        def collect_card(index, name, enchanted, quantity):
            parsed_cards.append({
                'index': index,
                'name': name,
                'enchanted': enchanted,
                'quantity': quantity
            })

        parse_dreamborn_list(deck_text, collect_card)

        assert len(parsed_cards) == 2
        assert parsed_cards[0]['name'] == "Anna - True-Hearted "
        assert parsed_cards[0]['enchanted'] == True
        assert parsed_cards[1]['enchanted'] == False

    def test_parse_dreamborn_with_x_quantity(self):
        """Test parsing Dreamborn format with 'x' in quantity."""
        deck_text = """4x Pete - Games Referee
3x Merlin, Goat"""

        parsed_cards = []
        def collect_card(index, name, enchanted, quantity):
            parsed_cards.append({
                'index': index,
                'name': name,
                'quantity': quantity
            })

        parse_dreamborn_list(deck_text, collect_card)

        assert len(parsed_cards) == 2
        assert parsed_cards[0]['name'] == "Pete - Games Referee"
        assert parsed_cards[0]['quantity'] == 4


# --- Unit Tests for Utility Functions ---

class TestUtilityFunctions:
    """Test utility functions."""

    def test_remove_nonalphanumeric(self):
        """Test removing non-alphanumeric characters."""
        assert remove_nonalphanumeric("Elsa, Spirit of Winter") == "ElsaSpiritofWinter"
        assert remove_nonalphanumeric("Anna - True-Hearted") == "AnnaTrueHearted"
        assert remove_nonalphanumeric("Magic Broom") == "MagicBroom"

    def test_format_lorcast_query(self):
        """Test Lorcast query formatting."""
        query = format_lorcast_query("Elsa, Spirit of Winter", False)
        assert "+" in query
        assert "rarity:enchanted" not in query

        query_enchanted = format_lorcast_query("Anna - True-Hearted", True)
        assert "rarity:enchanted" in query_enchanted


# --- Integration Tests for API and Image Fetching ---

@pytest.mark.integration
class TestLorcastAPI:
    """Test Lorcast API requests."""

    def test_lorcast_api_availability(self):
        """Test that Lorcast API is available and responding."""
        response = request_lorcast("https://api.lorcast.com/v0/cards/search?q=Elsa")
        assert response.status_code == 200
        json_data = response.json()
        assert 'results' in json_data


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
        """Test fetching a single Lorcana card."""
        front_dir = temp_dirs

        # Use a very small decklist - just 1 card
        deck_text = "1 Elsa, Spirit of Winter"

        handle_card = get_handle_card(front_dir)
        parse_deck(deck_text, DeckFormat.DREAMBORN, handle_card)

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

        deck_text = "2 Magic Broom, Illuminary Keeper"

        handle_card = get_handle_card(front_dir)
        parse_deck(deck_text, DeckFormat.DREAMBORN, handle_card)

        # Should have 2 copies of the card
        files = os.listdir(front_dir)
        assert len(files) == 2

        for f in files:
            file_path = os.path.join(front_dir, f)
            assert os.path.getsize(file_path) > 0
