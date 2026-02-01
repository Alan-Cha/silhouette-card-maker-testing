"""
Tests for the Star Wars Unlimited plugin.
Tests deck format parsing and image fetching from SWUDB.
"""
import os
import shutil
import tempfile
import pytest

from plugins.star_wars_unlimited.deck_formats import DeckFormat, parse_deck, parse_melee, parse_picklist, parse_swudb_json
from plugins.star_wars_unlimited.swudb import (
    request_swudb,
    get_handle_card,
    fetch_name_and_title,
    SWUDB_CARD_NUMBER_URL_TEMPLATE,
)


# --- Unit Tests for Deck Format Parsing ---

class TestMeleeFormat:
    """Test Melee format parsing."""

    def test_parse_melee_basic(self):
        """Test parsing basic Melee format."""
        deck_text = """Leaders
1 | Han Solo | Audacious Smuggler

Base
1 | Level 1313

Deck
3 | Hotshot DL-44 Blaster
3 | L3-37 | Droid Revolutionary"""

        parsed_cards = []
        def collect_card(index, name, title, quantity):
            parsed_cards.append({
                'index': index,
                'name': name,
                'title': title,
                'quantity': quantity
            })

        parse_melee(deck_text, collect_card)

        assert len(parsed_cards) == 4
        assert parsed_cards[0]['name'] == "Han Solo"
        assert parsed_cards[0]['title'] == "Audacious Smuggler"
        assert parsed_cards[1]['name'] == "Level 1313"
        assert parsed_cards[1]['title'] == ""  # Bases don't have titles

    def test_parse_melee_with_sideboard(self):
        """Test parsing Melee format with sideboard."""
        deck_text = """Deck
3 | Cunning
2 | Cantina Bouncer

Sideboard
1 | Moisture Farmer
2 | A New Adventure"""

        parsed_cards = []
        def collect_card(index, name, title, quantity):
            parsed_cards.append({
                'index': index,
                'name': name,
                'quantity': quantity
            })

        parse_melee(deck_text, collect_card)

        assert len(parsed_cards) == 4


class TestPicklistFormat:
    """Test Picklist format parsing."""

    def test_parse_picklist_basic(self):
        """Test parsing Picklist format."""
        deck_text = """[ ]          Han Solo | Audacious Smuggler
             SOR 017, SOR 283, SOR 267

[ ] [ ] [ ]  Millennium Falcon | Piece of Junk
             SOR 193, SOR 455"""

        parsed_cards = []
        def collect_card(index, name, title, quantity):
            parsed_cards.append({
                'index': index,
                'name': name,
                'title': title,
                'quantity': quantity
            })

        parse_picklist(deck_text, collect_card)

        assert len(parsed_cards) == 2
        assert parsed_cards[0]['name'] == "Han Solo"
        assert parsed_cards[0]['quantity'] == 1
        assert parsed_cards[1]['name'] == "Millennium Falcon"
        assert parsed_cards[1]['quantity'] == 3


class TestSwudbJsonFormat:
    """Test SWUDB JSON format parsing."""

    def test_parse_swudb_json_basic(self):
        """Test parsing SWUDB JSON format."""
        deck_text = """{
  "leader": {"id": "SOR_017", "count": 1},
  "base": {"id": "TWI_029", "count": 1},
  "deck": [
    {"id": "SOR_203", "count": 3},
    {"id": "SHD_202", "count": 3}
  ],
  "sideboard": []
}"""

        parsed_cards = []
        def collect_card(index, name, title, quantity):
            parsed_cards.append({
                'index': index,
                'name': name,
                'title': title,
                'quantity': quantity
            })

        parse_swudb_json(deck_text, collect_card)

        # Should parse leader, base, and deck cards
        assert len(parsed_cards) >= 4


# --- Unit Tests for Data Corrections ---

class TestDataCorrections:
    """Test data correction logic."""

    def test_tyrannus_typo_correction(self):
        """Test that SWUDB's Darth Tyrannus typo is corrected to Tyranus."""
        # SWUDB incorrectly returns subtitle Darth Tyrannus for Count Dooku card
        # The correct subtitle is Darth Tyranus
        json = request_swudb(SWUDB_CARD_NUMBER_URL_TEMPLATE.format(set_id="SOR", set_number="304")).json()
        raw_name = json.get('Name')
        raw_title = json.get('Subtitle') or '' if json.get('Type') != 'Base' else ''
        assert raw_name == "Count Dooku"
        assert raw_title == "Darth Tyrannus"  # Raw data has typo

        name, title = fetch_name_and_title("SOR_304")
        assert name == "Count Dooku"
        assert title == "Darth Tyranus"  # Corrected spelling


# --- Integration Tests for API and Image Fetching ---

class TestSwudbAPI:
    """Test SWUDB API requests."""

    def test_swudb_api_availability(self):
        """Test that SWUDB API is available and responding."""
        response = request_swudb(SWUDB_CARD_NUMBER_URL_TEMPLATE.format(set_id="SOR", set_number="017"))
        assert response.status_code == 200

        json_data = response.json()
        assert json_data.get('Name') == "Han Solo"

    def test_fetch_name_and_title(self):
        """Test fetching card name and title from card ID."""
        name, title = fetch_name_and_title("SOR_017")
        assert name == "Han Solo"
        assert title == "Audacious Smuggler"

    def test_fetch_name_and_title_base_card(self):
        """Test fetching name for a base card (no title)."""
        name, title = fetch_name_and_title("TWI_029")
        # Base cards should have empty title
        assert name != ""
        assert title == ""


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

    def test_fetch_single_card_melee(self, temp_dirs):
        """Test fetching a single card using Melee format."""
        front_dir, double_sided_dir = temp_dirs

        # Use a very small decklist - just 1 card
        deck_text = """Deck
1 | Cunning"""

        handle_card = get_handle_card(front_dir, double_sided_dir)
        parse_deck(deck_text, DeckFormat.MELEE, handle_card)

        # Check that at least one image was created
        files = os.listdir(front_dir)
        assert len(files) >= 1

        # Verify image file has content (> 0 bytes)
        for f in files:
            file_path = os.path.join(front_dir, f)
            assert os.path.getsize(file_path) > 0

    def test_fetch_card_with_title(self, temp_dirs):
        """Test fetching a card with name and title."""
        front_dir, double_sided_dir = temp_dirs

        deck_text = """Deck
1 | Han Solo | Audacious Smuggler"""

        handle_card = get_handle_card(front_dir, double_sided_dir)
        parse_deck(deck_text, DeckFormat.MELEE, handle_card)

        files = os.listdir(front_dir)
        assert len(files) >= 1

        for f in files:
            file_path = os.path.join(front_dir, f)
            assert os.path.getsize(file_path) > 0

    def test_fetch_with_quantity(self, temp_dirs):
        """Test fetching cards with quantity > 1."""
        front_dir, double_sided_dir = temp_dirs

        deck_text = """Deck
2 | Cunning"""

        handle_card = get_handle_card(front_dir, double_sided_dir)
        parse_deck(deck_text, DeckFormat.MELEE, handle_card)

        # Should have 2 copies of the card
        files = os.listdir(front_dir)
        assert len(files) == 2

        for f in files:
            file_path = os.path.join(front_dir, f)
            assert os.path.getsize(file_path) > 0
