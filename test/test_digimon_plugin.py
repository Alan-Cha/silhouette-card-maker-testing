"""
Tests for the Digimon plugin.
Tests deck format parsing and image fetching from digimoncard.io.
"""
import os
import shutil
import tempfile
import pytest

from plugins.digimon.deck_formats import (
    DeckFormat,
    parse_deck,
    parse_tts,
    parse_digimoncardio,
    parse_digimoncardapp,
    parse_digimonmeta,
    parse_untap,
)
from plugins.digimon.digimoncard import request_digimon, get_handle_card


# --- Unit Tests for Deck Format Parsing ---

class TestTTSFormat:
    """Test Tabletop Simulator format parsing."""

    def test_parse_tts(self):
        """Test parsing TTS format (Python list as string)."""
        deck_text = '["BT15-006","BT15-006","BT2-070"]'

        parsed_cards = []
        def collect_card(index, card_code, quantity):
            parsed_cards.append({
                'index': index,
                'card_code': card_code,
                'quantity': quantity
            })

        parse_tts(deck_text, collect_card)

        assert len(parsed_cards) == 3
        assert parsed_cards[0]['card_code'] == "BT15-006"


class TestDigimoncardioFormat:
    """Test digimoncard.io format parsing."""

    def test_parse_digimoncardio(self):
        """Test parsing digimoncard.io format."""
        deck_text = """// Digimon Deck List
4 BlitzGreymon EX9-013
2 Blue Scramble LM-028
4 Gabumon BT15-020"""

        parsed_cards = []
        def collect_card(index, card_code, quantity):
            parsed_cards.append({
                'index': index,
                'card_code': card_code,
                'quantity': quantity
            })

        parse_digimoncardio(deck_text, collect_card)

        assert len(parsed_cards) == 3
        assert parsed_cards[0]['card_code'] == "EX9-013"
        assert parsed_cards[1]['card_code'] == "LM-028"
        assert parsed_cards[2]['card_code'] == "BT15-020"


class TestDigimoncardappFormat:
    """Test digimoncard.app format parsing."""

    def test_parse_digimoncardapp(self):
        """Test parsing digimoncard.app format."""
        deck_text = """// Digimon DeckList

BT11-005 Koromon 4
EX10-006 Agumon 4
BT8-058 Agumon 4"""

        parsed_cards = []
        def collect_card(index, card_code, quantity):
            parsed_cards.append({
                'index': index,
                'card_code': card_code,
                'quantity': quantity
            })

        parse_digimoncardapp(deck_text, collect_card)

        assert len(parsed_cards) == 3
        assert parsed_cards[0]['card_code'] == "BT11-005"
        assert parsed_cards[1]['card_code'] == "EX10-006"


class TestDigimonmetaFormat:
    """Test DigimonMeta format parsing."""

    def test_parse_digimonmeta(self):
        """Test parsing DigimonMeta format."""
        deck_text = """4 (BT22-002)
4 (ST19-03)
2 (EX7-024)"""

        parsed_cards = []
        def collect_card(index, card_code, quantity):
            parsed_cards.append({
                'index': index,
                'card_code': card_code,
                'quantity': quantity
            })

        parse_digimonmeta(deck_text, collect_card)

        assert len(parsed_cards) == 3
        assert parsed_cards[0]['card_code'] == "BT22-002"
        assert parsed_cards[1]['card_code'] == "ST19-03"


class TestUntapFormat:
    """Test Untap format parsing."""

    def test_parse_untap(self):
        """Test parsing Untap format."""
        deck_text = """1 MetalTyrannomon                      (DCG) (BT11-055)
4 Analogman                            (DCG) (BT11-092)
1 Chaosdramon (X Antibody)             (DCG) (BT12-072)"""

        parsed_cards = []
        def collect_card(index, card_code, quantity):
            parsed_cards.append({
                'index': index,
                'card_code': card_code,
                'quantity': quantity
            })

        parse_untap(deck_text, collect_card)

        assert len(parsed_cards) == 3
        assert parsed_cards[0]['card_code'] == "BT11-055"
        assert parsed_cards[0]['quantity'] == 1
        assert parsed_cards[1]['card_code'] == "BT11-092"
        assert parsed_cards[1]['quantity'] == 4


# --- Integration Tests for API and Image Fetching ---

class TestDigimonAPI:
    """Test Digimon API requests."""

    def test_digimon_api_availability(self):
        """Test that Digimon API is available and responding."""
        response = request_digimon("https://digimoncard.io/api-public/search.php?card=BT15-006")
        assert response.status_code == 200


class TestFullFetchWorkflow:
    """Integration tests for the complete card fetching workflow."""

    @pytest.fixture
    def temp_dirs(self):
        """Create temporary directories for test output."""
        front_dir = tempfile.mkdtemp()
        yield front_dir
        shutil.rmtree(front_dir)

    def test_fetch_single_card_digimoncardio(self, temp_dirs):
        """Test fetching a single card using digimoncardio format."""
        front_dir = temp_dirs

        # Use a very small decklist - just 1 card
        deck_text = "1 Agumon BT1-010"

        handle_card = get_handle_card(front_dir)
        parse_deck(deck_text, DeckFormat.DIGIMONCARDIO, handle_card)

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

        deck_text = "2 Agumon BT1-010"

        handle_card = get_handle_card(front_dir)
        parse_deck(deck_text, DeckFormat.DIGIMONCARDIO, handle_card)

        # Should have 2 copies of the card
        files = os.listdir(front_dir)
        assert len(files) == 2

        for f in files:
            file_path = os.path.join(front_dir, f)
            assert os.path.getsize(file_path) > 0
